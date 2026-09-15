import asyncio
import json
import logging
import os
import random
from typing import Type, TypeVar, Optional, Tuple, Any
from pydantic import BaseModel, ValidationError

import httpx
from google import genai
from google.genai import types
from google.genai.errors import APIError, ClientError, ServerError

from app.core.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMServiceError(Exception):
    """Base exception for LLM service errors."""
    pass


class LLMKeyMissingError(LLMServiceError):
    """Raised when Gemini API key is missing or not configured."""
    pass


class LLMAPIError(LLMServiceError):
    """Raised when Gemini API invocation fails due to network, rate limit, or API error."""
    pass


class LLMParseError(LLMServiceError):
    """Raised when LLM output cannot be parsed or validated against expected schema."""
    pass


class LLMService:
    """
    Robust service encapsulating interactions with Google Gemini API.
    
    Includes:
    - Automatic retries for transient errors (503 UNAVAILABLE, 429 RESOURCE_EXHAUSTED, 500, timeouts)
    - Exponential backoff with randomized jitter
    - Configurable primary and fallback models (e.g. gemini-2.5-flash -> gemini-2.0-flash)
    - Clean user-facing error messages without exposing raw Python tracebacks or API keys
    - Detailed, sanitized backend logging
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        fallback_model: Optional[str] = None,
        max_retries: Optional[int] = None,
        retry_initial_delay: Optional[float] = None,
        retry_backoff_factor: Optional[float] = None,
        retry_jitter: Optional[float] = None,
    ):
        self.api_key = api_key if api_key is not None else (settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY"))
        self.model = model or getattr(settings, "GEMINI_MODEL", "gemini-2.5-flash")
        self.fallback_model = fallback_model if fallback_model is not None else getattr(settings, "GEMINI_FALLBACK_MODEL", "gemini-2.0-flash")
        self.max_retries = max_retries if max_retries is not None else getattr(settings, "GEMINI_MAX_RETRIES", 4)
        self.retry_initial_delay = retry_initial_delay if retry_initial_delay is not None else getattr(settings, "GEMINI_RETRY_INITIAL_DELAY", 1.0)
        self.retry_backoff_factor = retry_backoff_factor if retry_backoff_factor is not None else getattr(settings, "GEMINI_RETRY_BACKOFF_FACTOR", 2.0)
        self.retry_jitter = retry_jitter if retry_jitter is not None else getattr(settings, "GEMINI_RETRY_JITTER", 0.5)

    def _get_client(self) -> genai.Client:
        key = self.api_key.strip() if self.api_key else ""
        if not key or key.lower() in [
            "your_gemini_api_key_here",
            "your_api_key_here", 
            "your-gemini-api-key",
            "none"
        ] or key.startswith("your_"):
            raise LLMKeyMissingError("Gemini API key is missing or not configured.")
        return genai.Client(api_key=key)

    def _is_transient_error(self, exc: Exception) -> Tuple[bool, Optional[int], str]:
        """
        Determines whether an exception represents a transient failure eligible for retry.
        
        Eligible errors include:
        - HTTP 503 UNAVAILABLE (model overloaded / capacity spikes)
        - HTTP 429 RESOURCE_EXHAUSTED (rate limits)
        - HTTP 500, 502, 504 (transient gateway/server glitches)
        - Network connection/timeout exceptions (httpx errors)
        """
        if isinstance(exc, APIError):
            code = getattr(exc, "code", None)
            status_text = str(getattr(exc, "status", "") or "").upper()
            msg = str(getattr(exc, "message", "") or str(exc))

            if code in [503, 429, 500, 502, 504]:
                return True, code, f"{code} {status_text or 'API_ERROR'}"

            if "503" in msg or "UNAVAILABLE" in msg or "high demand" in msg.lower():
                return True, 503, "503 UNAVAILABLE"
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg or "rate limit" in msg.lower() or "quota" in msg.lower():
                return True, 429, "429 RESOURCE_EXHAUSTED"
            if "500" in msg or "INTERNAL" in msg:
                return True, 500, "500 INTERNAL_SERVER_ERROR"

            return False, code, f"{code} {status_text or 'CLIENT_OR_SERVER_ERROR'}"

        if isinstance(exc, (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError)):
            return True, None, exc.__class__.__name__

        # General check for transient network/connection error messages
        exc_str = str(exc).lower()
        if "503" in exc_str or "unavailable" in exc_str or "high demand" in exc_str:
            return True, 503, "503 UNAVAILABLE"
        if "429" in exc_str or "resource_exhausted" in exc_str or "rate limit" in exc_str:
            return True, 429, "429 RESOURCE_EXHAUSTED"
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
        client: genai.Client,
        model_name: str,
        prompt: str,
        config: types.GenerateContentConfig,
    ) -> Any:
        """Invokes the Google GenAI SDK model generation."""
        return await client.aio.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config,
        )

    async def _attempt_generate_with_model(
        self,
        client: genai.Client,
        model_name: str,
        prompt: str,
        config: types.GenerateContentConfig,
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
                    prompt=prompt,
                    config=config,
                )

                if not response or not getattr(response, "text", None):
                    raise LLMParseError("Gemini returned an empty completion response.")

                raw_text = response.text.strip()
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
                        "Gemini request on model '%s' attempt %d/%d encountered transient error [%s]. Retrying in %.2fs...",
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
                        "Non-retryable Gemini error on model '%s' (attempt %d/%d): %s",
                        model_name,
                        attempt,
                        max_attempts,
                        error_reason,
                    )
                    raise

                logger.error(
                    "Gemini transient failure exhausted retries for model '%s' (attempt %d/%d). Error: %s",
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
        Sends prompt to Gemini API with robust retries, exponential backoff, and fallback model.
        Returns validated Pydantic model response.
        """
        client = self._get_client()

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            response_schema=response_model,
            temperature=0.0,
        )

        # 1. Try Primary Model with automatic retries
        try:
            return await self._attempt_generate_with_model(
                client=client,
                model_name=self.model,
                prompt=prompt,
                config=config,
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
                        prompt=prompt,
                        config=config,
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
                "Gemini AI generation failed across configured models (primary='%s', fallback='%s').",
                self.model,
                self.fallback_model or "none",
            )
            # Clean user-facing error message without leaking API keys or internal stack traces
            raise LLMAPIError(
                "The AI analysis service is temporarily experiencing high demand. Please try again shortly."
            ) from primary_err


# Singleton default instance
default_llm_service = LLMService()
