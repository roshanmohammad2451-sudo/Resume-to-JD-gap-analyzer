import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from pydantic import BaseModel
import httpx
from openai import (
    APIError,
    RateLimitError,
    InternalServerError,
    APITimeoutError,
    APIConnectionError,
    AuthenticationError,
)

from app.services.llm_service import (
    LLMService,
    LLMKeyMissingError,
    LLMAPIError,
    LLMParseError,
)


class MockOutputSchema(BaseModel):
    summary: str
    score: int


def _create_mock_completion_response(content: str):
    mock_choice = MagicMock()
    mock_choice.message.content = content
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    return mock_response


# 1. Successful structured output generation
@pytest.mark.asyncio
async def test_groq_successful_generation():
    service = LLMService(
        api_key="gsk_valid_test_key", 
        model="openai/gpt-oss-120b", 
        base_url="https://api.groq.com/openai/v1",
        max_retries=3
    )

    mock_resp = _create_mock_completion_response('{"summary": "Test passed", "score": 100}')

    with patch.object(service, "_execute_generate_content", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = mock_resp

        res = await service.generate_structured_output(
            prompt="Hello",
            system_prompt="System",
            response_model=MockOutputSchema,
        )

        assert res.summary == "Test passed"
        assert res.score == 100
        assert mock_exec.call_count == 1


# 2. Markdown JSON code fence stripping
@pytest.mark.asyncio
async def test_groq_code_fence_stripping():
    service = LLMService(
        api_key="gsk_valid_test_key", 
        model="openai/gpt-oss-120b",
        max_retries=2
    )

    mock_resp = _create_mock_completion_response('```json\n{"summary": "Markdown fenced", "score": 95}\n```')

    with patch.object(service, "_execute_generate_content", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = mock_resp

        res = await service.generate_structured_output(
            prompt="Hello",
            system_prompt="System",
            response_model=MockOutputSchema,
        )

        assert res.summary == "Markdown fenced"
        assert res.score == 95


# 3. Invalid/malformed model output raises LLMParseError
@pytest.mark.asyncio
async def test_groq_malformed_json_raises_parse_error():
    service = LLMService(
        api_key="gsk_valid_test_key", 
        model="openai/gpt-oss-120b",
        max_retries=2
    )

    mock_resp = _create_mock_completion_response('This is not valid json at all!')

    with patch.object(service, "_execute_generate_content", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = mock_resp

        with pytest.raises(LLMParseError) as exc_info:
            await service.generate_structured_output(
                prompt="Hello",
                system_prompt="System",
                response_model=MockOutputSchema,
            )

        assert "Failed to validate LLM response against schema" in str(exc_info.value)


# 4. Empty completion output raises LLMParseError
@pytest.mark.asyncio
async def test_groq_empty_completion_raises_parse_error():
    service = LLMService(
        api_key="gsk_valid_test_key", 
        model="openai/gpt-oss-120b",
        max_retries=2
    )

    mock_response = MagicMock()
    mock_response.choices = []

    with patch.object(service, "_execute_generate_content", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = mock_response

        with pytest.raises(LLMParseError) as exc_info:
            await service.generate_structured_output(
                prompt="Hello",
                system_prompt="System",
                response_model=MockOutputSchema,
            )

        assert "empty completion response" in str(exc_info.value)


# 5. Missing or placeholder GROQ_API_KEY
@pytest.mark.asyncio
async def test_groq_missing_api_key_raises():
    service = LLMService(api_key="")
    with pytest.raises(LLMKeyMissingError) as exc_info:
        await service.generate_structured_output("prompt", "sys", MockOutputSchema)
    assert "Groq API key is missing" in str(exc_info.value)

    service_placeholder = LLMService(api_key="your_groq_api_key_here")
    with pytest.raises(LLMKeyMissingError) as exc_info:
        await service_placeholder.generate_structured_output("prompt", "sys", MockOutputSchema)
    assert "Groq API key is missing" in str(exc_info.value)


# 6. Transient 429 RateLimitError followed by successful retry
@pytest.mark.asyncio
async def test_groq_429_retry_success():
    service = LLMService(
        api_key="gsk_valid_test_key",
        model="openai/gpt-oss-120b",
        max_retries=3,
        retry_initial_delay=0.01,
        retry_jitter=0.0,
    )

    mock_req = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    mock_http_resp = httpx.Response(429, request=mock_req)
    err_429 = RateLimitError(message="Rate limit reached for requests per minute", response=mock_http_resp, body=None)
    mock_success = _create_mock_completion_response('{"summary": "Recovered from 429", "score": 85}')

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


# 7. Transient 503 InternalServerError followed by successful retry
@pytest.mark.asyncio
async def test_groq_503_retry_success():
    service = LLMService(
        api_key="gsk_valid_test_key",
        model="openai/gpt-oss-120b",
        max_retries=3,
        retry_initial_delay=0.01,
        retry_jitter=0.0,
    )

    mock_req = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    mock_http_resp = httpx.Response(503, request=mock_req)
    err_503 = InternalServerError(message="Service Unavailable / Model overloaded", response=mock_http_resp, body=None)
    mock_success = _create_mock_completion_response('{"summary": "Recovered from 503", "score": 90}')

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


# 8. Timeout / Network failure retry
@pytest.mark.asyncio
async def test_groq_timeout_network_failure_retry_success():
    service = LLMService(
        api_key="gsk_valid_test_key",
        model="openai/gpt-oss-120b",
        max_retries=3,
        retry_initial_delay=0.01,
        retry_jitter=0.0,
    )

    mock_req = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    err_timeout = APITimeoutError(request=mock_req)
    mock_success = _create_mock_completion_response('{"summary": "Recovered from timeout", "score": 88}')

    with patch.object(service, "_execute_generate_content", new_callable=AsyncMock) as mock_exec:
        mock_exec.side_effect = [err_timeout, mock_success]

        res = await service.generate_structured_output(
            prompt="Hello",
            system_prompt="System",
            response_model=MockOutputSchema,
        )

        assert res.summary == "Recovered from timeout"
        assert res.score == 88
        assert mock_exec.call_count == 2


# 9. Fallback model triggers on repeated transient failures
@pytest.mark.asyncio
async def test_groq_fallback_model_success_on_repeated_errors():
    service = LLMService(
        api_key="gsk_valid_test_key",
        model="openai/gpt-oss-120b",
        fallback_model="llama-3.3-70b-versatile",
        max_retries=2,
        retry_initial_delay=0.01,
        retry_jitter=0.0,
    )

    mock_req = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    mock_http_resp = httpx.Response(503, request=mock_req)
    err_503 = InternalServerError(message="Model overloaded", response=mock_http_resp, body=None)
    mock_fallback_success = _create_mock_completion_response('{"summary": "Fallback model worked", "score": 75}')

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
        calls = mock_exec.call_args_list
        assert calls[0].kwargs["model_name"] == "openai/gpt-oss-120b"
        assert calls[1].kwargs["model_name"] == "openai/gpt-oss-120b"
        assert calls[2].kwargs["model_name"] == "llama-3.3-70b-versatile"


# 10. Repeated failures across all retries raise clean sanitized LLMAPIError
@pytest.mark.asyncio
async def test_groq_repeated_failures_raise_sanitized_error():
    service = LLMService(
        api_key="gsk_valid_test_key",
        model="openai/gpt-oss-120b",
        fallback_model="llama-3.3-70b-versatile",
        max_retries=2,
        retry_initial_delay=0.01,
        retry_jitter=0.0,
    )

    mock_req = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    mock_http_resp = httpx.Response(503, request=mock_req)
    err_503 = InternalServerError(message="gsk_SECRET_KEY_DO_NOT_LEAK internal failure", response=mock_http_resp, body=None)

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
        # Verify secret key or internal leak is NOT present
        assert "gsk_SECRET_KEY" not in err_message


# 11. Non-retryable error (e.g. 401 AuthenticationError) fails fast without retrying
@pytest.mark.asyncio
async def test_groq_non_transient_error_fails_fast():
    service = LLMService(
        api_key="gsk_invalid_test_key",
        model="openai/gpt-oss-120b",
        max_retries=3,
        retry_initial_delay=0.01,
    )

    mock_req = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    mock_http_resp = httpx.Response(401, request=mock_req)
    err_401 = AuthenticationError(message="Invalid API Key", response=mock_http_resp, body=None)

    with patch.object(service, "_execute_generate_content", new_callable=AsyncMock) as mock_exec:
        mock_exec.side_effect = err_401

        with pytest.raises(LLMAPIError):
            await service.generate_structured_output(
                prompt="Hello",
                system_prompt="System",
                response_model=MockOutputSchema,
            )

        # Fails fast on attempt 1 without retrying
        assert mock_exec.call_count == 1


# 12. Correct model and Groq endpoint configuration
def test_groq_model_and_endpoint_configuration():
    service = LLMService(
        api_key="gsk_sample_key",
        model="openai/gpt-oss-120b",
        base_url="https://api.groq.com/openai/v1",
    )
    client = service._get_client()
    assert client.api_key == "gsk_sample_key"
    assert str(client.base_url).rstrip("/") == "https://api.groq.com/openai/v1"
    assert service.model == "openai/gpt-oss-120b"

