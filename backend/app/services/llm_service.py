import asyncio
import json
import logging
import os
import random
from typing import Type, TypeVar, Optional, Tuple, Any
from pydantic import BaseModel, ValidationError

import httpx
from openai import (
    AsyncOpenAI,
    APIError,
    RateLimitError,
    InternalServerError,
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
)

from app.core.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMServiceError(Exception):
    """Base exception for LLM service errors."""
    pass


class LLMKeyMissingError(LLMServiceError):
    """Raised when Groq API key is missing or not configured."""
    pass


class LLMAPIError(LLMServiceError):
    """Raised when Groq API invocation fails due to network, rate limit, or API error."""
    pass


class LLMParseError(LLMServiceError):
    """Raised when LLM output cannot be parsed or validated against expected schema."""
    pass


class LLMService:
    """
    Robust service encapsulating interactions with Groq's OpenAI-compatible API.
    
    Includes:
    - Automatic retries for transient errors (429 RateLimit, 503 UNAVAILABLE, 500, 502, 504, timeouts)
    - Exponential backoff with randomized jitter
    - Configurable primary and fallback models (e.g. openai/gpt-oss-120b -> llama-3.3-70b-versatile)
    - Clean user-facing error messages without exposing raw Python tracebacks or API keys
    - Detailed, sanitized backend logging
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        fallback_model: Optional[str] = None,
        base_url: Optional[str] = None,
        max_retries: Optional[int] = None,
        retry_initial_delay: Optional[float] = None,
        retry_backoff_factor: Optional[float] = None,
        retry_jitter: Optional[float] = None,
    ):
        self.api_key = api_key if api_key is not None else (settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY"))
        self.model = model or getattr(settings, "GROQ_MODEL", "openai/gpt-oss-120b")
        self.fallback_model = fallback_model if fallback_model is not None else getattr(settings, "GROQ_FALLBACK_MODEL", None)
        self.base_url = base_url or getattr(settings, "GROQ_BASE_URL", "https://api.groq.com/openai/v1")
        self.max_retries = max_retries if max_retries is not None else getattr(settings, "GROQ_MAX_RETRIES", 4)
        self.retry_initial_delay = retry_initial_delay if retry_initial_delay is not None else getattr(settings, "GROQ_RETRY_INITIAL_DELAY", 1.0)
        self.retry_backoff_factor = retry_backoff_factor if retry_backoff_factor is not None else getattr(settings, "GROQ_RETRY_BACKOFF_FACTOR", 2.0)
        self.retry_jitter = retry_jitter if retry_jitter is not None else getattr(settings, "GROQ_RETRY_JITTER", 0.5)

    def _get_client(self) -> AsyncOpenAI:
        key = self.api_key.strip() if self.api_key else ""
        if not key or key.lower() in [
            "your_groq_api_key_here",
            "your_gemini_api_key_here",
            "your_api_key_here", 
            "your-groq-api-key",
            "none"
        ] or key.startswith("your_"):
            raise LLMKeyMissingError("Groq API key is missing or not configured.")
        return AsyncOpenAI(api_key=key, base_url=self.base_url)

    def _is_transient_error(self, exc: Exception) -> Tuple[bool, Optional[int], str]:
        """
        Determines whether an exception represents a transient failure eligible for retry.
        
        Eligible errors include:
        - HTTP 429 RateLimitError (rate limits / quota spikes)
        - HTTP 503, 500, 502, 504 InternalServerError (transient server issues)
        - Network connection/timeout exceptions (APIConnectionError, APITimeoutError, httpx errors)
        """
        if isinstance(exc, RateLimitError):
            return True, 429, "429 RATE_LIMIT_EXCEEDED"

        if isinstance(exc, InternalServerError):
            code = getattr(exc, "status_code", 500)
            return True, code, f"{code} SERVER_ERROR"

        if isinstance(exc, (APITimeoutError, APIConnectionError)):
            return True, None, exc.__class__.__name__

        if isinstance(exc, AuthenticationError):
            return False, 401, "401 AUTHENTICATION_ERROR"

        if isinstance(exc, APIError):
            code = getattr(exc, "status_code", None)
            msg = str(getattr(exc, "message", "") or str(exc))

            if code in [503, 429, 500, 502, 504]:
                return True, code, f"{code} API_ERROR"

            if "503" in msg or "unavailable" in msg.lower() or "overloaded" in msg.lower():
                return True, 503, "503 UNAVAILABLE"
            if "429" in msg or "rate limit" in msg.lower() or "quota" in msg.lower() or "tokens per minute" in msg.lower():
                return True, 429, "429 RATE_LIMIT_EXCEEDED"
            if "500" in msg or "internal" in msg.lower():
                return True, 500, "500 INTERNAL_SERVER_ERROR"

            return False, code, f"{code} CLIENT_OR_SERVER_ERROR"

        if isinstance(exc, (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError)):
            return True, None, exc.__class__.__name__

        # General check for transient network/connection error messages
        exc_str = str(exc).lower()
        if "503" in exc_str or "unavailable" in exc_str or "overloaded" in exc_str:
            return True, 503, "503 UNAVAILABLE"
        if "429" in exc_str or "rate limit" in exc_str or "quota" in exc_str:
            return True, 429, "429 RATE_LIMIT_EXCEEDED"
        if "timed out" in exc_str or "connection refused" in exc_str or "connection reset" in exc_str:
            return True, None, "ConnectionTimeoutOrReset"

        return False, None, exc.__class__.__name__

    def _calculate_backoff_delay(self, attempt: int) -> float:
        """
        Calculates exponential backoff with randomized jitter.
        Delay pattern for attempts 1, 2, 3, 4: ~1s, ~2s, ~4s, ~8s + jitter.
        """
        base_delay = self.retry_initial_delay * (self.retry_backoff_factor ** (attempt - 1))
        jitter = random.uniform(0.0, self.retry_jitter)
        return round(base_delay + jitter, 2)

    async def _execute_generate_content(
        self,
        client: AsyncOpenAI,
        model_name: str,
        system_prompt: str,
        prompt: str,
        response_model: Type[T],
    ) -> Any:
        """Invokes the Groq OpenAI-compatible Chat Completions API."""
        schema_json = json.dumps(response_model.model_json_schema(), indent=2)
        enforced_system_prompt = (
            f"{system_prompt}\n\n"
            f"You MUST output valid JSON strictly adhering to the following JSON schema:\n"
            f"{schema_json}\n"
            f"Return ONLY the raw JSON object without markdown formatting or code fences."
        )

        return await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": enforced_system_prompt},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
        )

    async def _attempt_generate_with_model(
        self,
        client: AsyncOpenAI,
        model_name: str,
        system_prompt: str,
        prompt: str,
        response_model: Type[T],
    ) -> T:
        """
        Attempts structured output generation with retries on transient errors.
        """
        max_attempts = max(1, self.max_retries)
        last_exception: Optional[Exception] = None
        last_error_summary = "Unknown error"

        for attempt in range(1, max_attempts + 1):
            try:
                response = await self._execute_generate_content(
                    client=client,
                    model_name=model_name,
                    system_prompt=system_prompt,
                    prompt=prompt,
                    response_model=response_model,
                )

                if not response or not getattr(response, "choices", None) or len(response.choices) == 0:
                    raise LLMParseError("Groq returned an empty completion response.")

                raw_text = response.choices[0].message.content
                if not raw_text or not raw_text.strip():
                    raise LLMParseError("Groq returned empty text content in completion.")

                raw_text = raw_text.strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.startswith("```"):
                    raw_text = raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                raw_text = raw_text.strip()

                try:
                    data = json.loads(raw_text)
                    return response_model.model_validate(data)
                except (json.JSONDecodeError, ValidationError) as ve:
                    raise LLMParseError(f"Failed to validate LLM response against schema: {str(ve)}") from ve

            except LLMKeyMissingError:
                raise
            except LLMParseError:
                # Schema validation issues should not be blindly retried with backoff
                raise
            except Exception as e:
                last_exception = e
                is_transient, status_code, error_reason = self._is_transient_error(e)
                last_error_summary = error_reason

                if is_transient and attempt < max_attempts:
                    delay = self._calculate_backoff_delay(attempt)
                    logger.warning(
                        "Groq request on model '%s' attempt %d/%d encountered transient error [%s]. Retrying in %.2fs...",
                        model_name,
                        attempt,
                        max_attempts,
                        error_reason,
                        delay,
                    )
                    await asyncio.sleep(delay)
                    continue

                if not is_transient:
                    logger.error(
                        "Non-retryable Groq error on model '%s' (attempt %d/%d): %s",
                        model_name,
                        attempt,
                        max_attempts,
                        error_reason,
                    )
                    raise

                logger.error(
                    "Groq transient failure exhausted retries for model '%s' (attempt %d/%d). Error: %s",
                    model_name,
                    attempt,
                    max_attempts,
                    error_reason,
                )
                break

        if last_exception:
            raise last_exception
        raise LLMAPIError(f"Generation failed for model '{model_name}'.")

    async def generate_structured_output(
        self, 
        prompt: str, 
        system_prompt: str, 
        response_model: Type[T]
    ) -> T:
        """
        Sends prompt to Groq API with robust retries, exponential backoff, and fallback model.
        Returns validated Pydantic model response.
        """
        client = self._get_client()

        # 1. Try Primary Model with automatic retries
        try:
            return await self._attempt_generate_with_model(
                client=client,
                model_name=self.model,
                system_prompt=system_prompt,
                prompt=prompt,
                response_model=response_model,
            )
        except (LLMKeyMissingError, LLMParseError):
            raise
        except Exception as primary_err:
            is_transient, status_code, error_reason = self._is_transient_error(primary_err)
            
            # 2. Try Fallback Model if available and different from primary
            if is_transient and self.fallback_model and self.fallback_model != self.model:
                logger.warning(
                    "Primary model '%s' unavailable after %d attempts (%s). Attempting fallback model '%s'...",
                    self.model,
                    self.max_retries,
                    error_reason,
                    self.fallback_model,
                )
                try:
                    return await self._attempt_generate_with_model(
                        client=client,
                        model_name=self.fallback_model,
                        system_prompt=system_prompt,
                        prompt=prompt,
                        response_model=response_model,
                    )
                except (LLMKeyMissingError, LLMParseError):
                    raise
                except Exception as fallback_err:
                    _, _, fb_error_reason = self._is_transient_error(fallback_err)
                    logger.error(
                        "Fallback model '%s' also failed (%s). Both primary and fallback models exhausted.",
                        self.fallback_model,
                        fb_error_reason,
                    )

            logger.error(
                "Groq AI generation failed across configured models (primary='%s', fallback='%s').",
                self.model,
                self.fallback_model or "none",
            )
            # Clean user-facing error message without leaking API keys or internal stack traces
            raise LLMAPIError(
                "The AI analysis service is temporarily experiencing high demand. Please try again shortly."
            ) from primary_err


# Singleton default instance
default_llm_service = LLMService()

