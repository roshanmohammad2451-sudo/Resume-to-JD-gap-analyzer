import hashlib
import logging
import math
import re
from typing import List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

EMBEDDING_DIM = 768


class EmbeddingService:
    """
    Embedding service providing semantic vectors for RAG knowledge retrieval.
    
    Uses Google Gemini text-embedding-004 when available and supported, and falls back
    to a deterministic normalized hash/frequency vector for offline tests or when API
    credentials are absent or unsupported.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_EMBEDDING_MODEL
        self._api_disabled = False

    def _is_valid_api_key(self) -> bool:
        if self._api_disabled or not self.api_key:
            return False
        key = self.api_key.strip().lower()
        return not (key in [
            "your_gemini_api_key_here",
            "your_openai_api_key_here",
            "your_api_key_here",
            "none",
            "",
            "test"
        ] or key.startswith("your_"))

    def get_deterministic_fallback_embedding(self, text: str, dim: int = EMBEDDING_DIM) -> List[float]:
        """
        Computes a deterministic normalized pseudo-semantic vector based on token hashes
        and n-grams. Used when offline or during test execution.
        """
        if not text:
            return [0.0] * dim

        vec = [0.0] * dim
        tokens = re.findall(r"\w+", text.lower())
        
        for token in tokens:
            # Word hash
            h = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16)
            idx = h % dim
            weight = 2.0 + (len(token) / 5.0)
            vec[idx] += weight

            # Bigram/trigram char hashes for morphological similarity
            for i in range(len(token) - 2):
                tri = token[i:i+3]
                th = int(hashlib.md5(tri.encode("utf-8")).hexdigest(), 16)
                tidx = th % dim
                vec[tidx] += 0.5

        # L2 normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [round(x / norm, 6) for x in vec]
        return vec

    async def get_embedding(self, text: str) -> List[float]:
        """
        Generates an embedding vector for the provided text.
        """
        clean_text = text.strip()
        if not clean_text:
            return [0.0] * EMBEDDING_DIM

        if self._is_valid_api_key():
            try:
                from google import genai
                client = genai.Client(api_key=self.api_key)
                response = await client.aio.models.embed_content(
                    model=self.model,
                    contents=clean_text,
                )
                if response and hasattr(response, "embedding") and response.embedding:
                    values = response.embedding.values
                    norm = math.sqrt(sum(v * v for v in values))
                    if norm > 0:
                        return [round(v / norm, 6) for v in values]
                    return values
                if response and hasattr(response, "embeddings") and response.embeddings:
                    values = response.embeddings[0].values
                    norm = math.sqrt(sum(v * v for v in values))
                    if norm > 0:
                        return [round(v / norm, 6) for v in values]
                    return values
            except Exception as e:
                logger.info(
                    "Gemini embedding API call not supported or unavailable (%s). Disabling API calls and using deterministic fallback.", 
                    str(e)
                )
                self._api_disabled = True

        return self.get_deterministic_fallback_embedding(clean_text)

    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embeddings for a batch of text chunks.
        """
        results = []
        for t in texts:
            emb = await self.get_embedding(t)
            results.append(emb)
        return results


default_embedding_service = EmbeddingService()
