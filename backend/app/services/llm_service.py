import json
import logging
import os
from typing import Type, TypeVar, Optional
from pydantic import BaseModel, ValidationError

from google import genai
from google.genai import types
from google.genai.errors import APIError

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
    """Service encapsulating interactions with Google Gemini API."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key if api_key is not None else (settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY"))
        self.model = model or settings.GEMINI_MODEL

    def _get_client(self) -> genai.Client:
        key = self.api_key.strip() if self.api_key else ""
        if not key or key.lower() in [
            "your_gemini_api_key_here",
            "your_openai_api_key_here",
            "your_api_key_here", 
            "your-gemini-api-key",
            "your-openai-api-key",
            "none"
        ] or key.startswith("your_"):
            raise LLMKeyMissingError("Gemini API key is missing or not configured.")
        return genai.Client(api_key=key)

    async def generate_structured_output(
        self, 
        prompt: str, 
        system_prompt: str, 
        response_model: Type[T]
    ) -> T:
        """
        Sends prompt to Gemini API and parses output strictly into the requested Pydantic model.
        """
        client = self._get_client()

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            response_schema=response_model,
            temperature=0.0,
        )

        try:
            response = await client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )

            if not response or not response.text:
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

        except APIError as e:
            logger.error("Gemini API Error: %s", e)
            raise LLMAPIError(f"Gemini service communication error: {str(e)}") from e
        except ValidationError as e:
            logger.error("Schema Validation Error: %s", e)
            raise LLMParseError(f"Response validation failed: {str(e)}") from e
        except LLMServiceError:
            raise
        except Exception as e:
            logger.error("Unexpected error in LLM service: %s", e)
            raise LLMServiceError(f"Unexpected error during AI generation: {str(e)}") from e


# Singleton default instance
default_llm_service = LLMService()

