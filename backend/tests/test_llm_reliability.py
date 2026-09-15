import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from pydantic import BaseModel
from google.genai.errors import APIError, ClientError, ServerError

from app.services.llm_service import (
    LLMService,
    LLMKeyMissingError,
    LLMAPIError,
    LLMParseError,
)


class MockOutputSchema(BaseModel):
    summary: str
    score: int


# 1. Successful structured output generation
@pytest.mark.asyncio
async def test_gemini_successful_generation():
    service = LLMService(api_key="valid-test-key", model="gemini-2.5-flash", max_retries=3)

    mock_response = MagicMock()
    mock_response.text = '{"summary": "Test passed", "score": 100}'

    with patch.object(service, "_execute_generate_content", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = mock_response

        res = await service.generate_structured_output(
            prompt="Hello",
            system_prompt="System",
            response_model=MockOutputSchema,
        )

        assert res.summary == "Test passed"
        assert res.score == 100
        assert mock_exec.call_count == 1


# 2. Transient 503 UNAVAILABLE followed by successful retry
@pytest.mark.asyncio
async def test_gemini_503_retry_success():
    service = LLMService(
        api_key="valid-test-key",
        model="gemini-2.5-flash",
        max_retries=3,
        retry_initial_delay=0.01,  # fast backoff in tests
        retry_jitter=0.0,
    )

    err_503 = APIError(503, {"error": {"code": 503, "status": "UNAVAILABLE", "message": "Model overloaded"}})
    mock_success = MagicMock()
    mock_success.text = '{"summary": "Recovered from 503", "score": 90}'

    with patch.object(service, "_execute_generate_content", new_callable=AsyncMock) as mock_exec:
        mock_exec.side_effect = [err_503, mock_success]

        res = await service.generate_structured_output(
            prompt="Hello",
            system_prompt="System",
            response_model=MockOutputSchema,
        )

        assert res.summary == "Recovered from 503"
        assert res.score == 90
        assert mock_exec.call_count == 2


# 3. Transient 429 RESOURCE_EXHAUSTED followed by successful retry
@pytest.mark.asyncio
async def test_gemini_429_retry_success():
    service = LLMService(
        api_key="valid-test-key",
        model="gemini-2.5-flash",
        max_retries=3,
        retry_initial_delay=0.01,
        retry_jitter=0.0,
    )

    err_429 = APIError(429, {"error": {"code": 429, "status": "RESOURCE_EXHAUSTED", "message": "Rate limit exceeded"}})
    mock_success = MagicMock()
    mock_success.text = '{"summary": "Recovered from 429", "score": 85}'

    with patch.object(service, "_execute_generate_content", new_callable=AsyncMock) as mock_exec:
        mock_exec.side_effect = [err_429, mock_success]

        res = await service.generate_structured_output(
            prompt="Hello",
            system_prompt="System",
            response_model=MockOutputSchema,
        )

        assert res.summary == "Recovered from 429"
        assert res.score == 85
        assert mock_exec.call_count == 2


# 4. Primary model repeated 503 errors triggers fallback model successfully
@pytest.mark.asyncio
async def test_gemini_fallback_model_success_on_repeated_503():
    service = LLMService(
        api_key="valid-test-key",
        model="gemini-2.5-flash",
        fallback_model="gemini-2.0-flash",
        max_retries=2,
        retry_initial_delay=0.01,
        retry_jitter=0.0,
    )

    err_503 = APIError(503, {"error": {"code": 503, "status": "UNAVAILABLE", "message": "Model overloaded"}})
    mock_fallback_success = MagicMock()
    mock_fallback_success.text = '{"summary": "Fallback model worked", "score": 75}'

    with patch.object(service, "_execute_generate_content", new_callable=AsyncMock) as mock_exec:
        # Primary model fails 2 times with 503, fallback model succeeds on first attempt
        mock_exec.side_effect = [err_503, err_503, mock_fallback_success]

        res = await service.generate_structured_output(
            prompt="Hello",
            system_prompt="System",
            response_model=MockOutputSchema,
        )

        assert res.summary == "Fallback model worked"
        assert res.score == 75
        assert mock_exec.call_count == 3
        # First 2 calls should be primary model, 3rd call should be fallback model
        calls = mock_exec.call_args_list
        assert calls[0].kwargs["model_name"] == "gemini-2.5-flash"
        assert calls[1].kwargs["model_name"] == "gemini-2.5-flash"
        assert calls[2].kwargs["model_name"] == "gemini-2.0-flash"


# 5. Repeated 503 failures across all retries and fallback models raise clean LLMAPIError
@pytest.mark.asyncio
async def test_gemini_repeated_503_raises_clean_error():
    service = LLMService(
        api_key="valid-test-key",
        model="gemini-2.5-flash",
        fallback_model="gemini-2.0-flash",
        max_retries=2,
        retry_initial_delay=0.01,
        retry_jitter=0.0,
    )

    err_503 = APIError(503, {"error": {"code": 503, "status": "UNAVAILABLE", "message": "SecretKey=AIzaSyA_INTERNAL_KEY_DO_NOT_LEAK"}})

    with patch.object(service, "_execute_generate_content", new_callable=AsyncMock) as mock_exec:
        mock_exec.side_effect = err_503

        with pytest.raises(LLMAPIError) as exc_info:
            await service.generate_structured_output(
                prompt="Hello",
                system_prompt="System",
                response_model=MockOutputSchema,
            )

        err_message = str(exc_info.value)
        # Verify clean user-facing error message
        assert "temporarily experiencing high demand" in err_message
        # Verify API key or raw stack trace details are NOT in the message
        assert "SecretKey" not in err_message
        assert "AIzaSyA" not in err_message


# 6. Non-retryable error (e.g. 400 Bad Request) fails immediately without retry
@pytest.mark.asyncio
async def test_gemini_non_transient_error_fails_fast():
    service = LLMService(
        api_key="valid-test-key",
        model="gemini-2.5-flash",
        max_retries=3,
        retry_initial_delay=0.01,
    )

    err_400 = APIError(400, {"error": {"code": 400, "status": "INVALID_ARGUMENT", "message": "Bad request"}})

    with patch.object(service, "_execute_generate_content", new_callable=AsyncMock) as mock_exec:
        mock_exec.side_effect = err_400

        with pytest.raises(LLMAPIError):
            await service.generate_structured_output(
                prompt="Hello",
                system_prompt="System",
                response_model=MockOutputSchema,
            )

        # Fails fast on attempt 1 without retrying
        assert mock_exec.call_count == 1
