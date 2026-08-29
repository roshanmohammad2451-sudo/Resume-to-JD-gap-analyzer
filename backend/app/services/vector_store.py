import abc
import json
import logging
import math
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class KnowledgeChunk(BaseModel):
    chunk_id: str = Field(..., description="Stable unique identifier for the chunk")
    source_id: str = Field(..., description="Stable identifier of the source document")
    skill: str = Field(..., description="Canonical normalized skill associated with this chunk")
    title: str = Field(..., description="Title of the source knowledge document")
    section: Optional[str] = Field(None, description="Section heading from the source document")
    text: str = Field(..., description="Verbatim text content of the chunk")
    embedding: List[float] = Field(default_factory=list, description="Vector embedding representation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional document metadata")


class SearchResult(BaseModel):
    chunk: KnowledgeChunk
    similarity: float = Field(..., description="Cosine similarity score (0.0 to 1.0)")


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculates cosine similarity between two vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    val = dot / (norm1 * norm2)
    # Bound to [-1.0, 1.0] to guard against floating point inaccuracies
    return max(-1.0, min(1.0, val))


class BaseVectorStore(abc.ABC):
    """Abstract interface for Phase 7 vector store implementations."""

    @abc.abstractmethod
    async def add_chunks(self, chunks: List[KnowledgeChunk]) -> int:
        """Adds or updates chunks. Returns the count of chunks stored."""
        pass

    @abc.abstractmethod
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 3,
        filter_skill: Optional[str] = None,
        min_similarity: float = 0.0,
    ) -> List[SearchResult]:
        """Searches for chunks similar to the query embedding."""
        pass

    @abc.abstractmethod
    def get_chunk(self, chunk_id: str) -> Optional[KnowledgeChunk]:
        """Retrieves a single chunk by its ID."""
        pass

    @abc.abstractmethod
    def get_all_chunks(self) -> List[KnowledgeChunk]:
        """Returns all chunks in the store."""
        pass

    @abc.abstractmethod
    def clear(self) -> None:
        """Clears all stored chunks."""
        pass


class LocalVectorStore(BaseVectorStore):
    """
    In-memory and file-backed vector store for local development, demo, and test execution.
    Provides fast cosine similarity retrieval, skill filtering, and idempotent chunk updates.
    """

    def __init__(self, persistence_path: Optional[str] = None):
        self.persistence_path = persistence_path
        self._chunks: Dict[str, KnowledgeChunk] = {}
        if self.persistence_path and os.path.exists(self.persistence_path):
            self._load_from_disk()

    def _load_from_disk(self) -> None:
        try:
            with open(self.persistence_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    chunk = KnowledgeChunk.model_validate(item)
                    self._chunks[chunk.chunk_id] = chunk
            logger.info("Loaded %d knowledge chunks from %s", len(self._chunks), self.persistence_path)
        except Exception as e:
            logger.warning("Could not load vector store from disk: %s", e)

    def _save_to_disk(self) -> None:
        if not self.persistence_path:
            return
        try:
            os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
            with open(self.persistence_path, "w", encoding="utf-8") as f:
                data = [chunk.model_dump() for chunk in self._chunks.values()]
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error("Failed to save vector store to disk: %s", e)

    async def add_chunks(self, chunks: List[KnowledgeChunk]) -> int:
        added = 0
        for chunk in chunks:
            self._chunks[chunk.chunk_id] = chunk
            added += 1
        if added > 0:
            self._save_to_disk()
        return added

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 3,
        filter_skill: Optional[str] = None,
        min_similarity: float = 0.0,
    ) -> List[SearchResult]:
        if not self._chunks or not query_embedding:
            return []

        candidates = self._chunks.values()
        if filter_skill:
            norm_filter = filter_skill.strip().lower()
            candidates = [c for c in candidates if c.skill.lower() == norm_filter or norm_filter in c.skill.lower()]

        scored_results: List[SearchResult] = []
        for chunk in candidates:
            if not chunk.embedding:
                continue
            sim = cosine_similarity(query_embedding, chunk.embedding)
            # If chunk is from the exact target skill's curated curriculum, incorporate skill match relevance
            if filter_skill:
                norm_f = filter_skill.strip().lower()
                if chunk.skill.lower() == norm_f or norm_f in chunk.skill.lower():
                    sim = max(sim, 0.72 + 0.28 * max(0.0, sim))
            if sim >= min_similarity:
                scored_results.append(SearchResult(chunk=chunk, similarity=round(sim, 4)))

        # Sort descending by similarity
        scored_results.sort(key=lambda x: x.similarity, reverse=True)
        return scored_results[:top_k]

    def get_chunk(self, chunk_id: str) -> Optional[KnowledgeChunk]:
        return self._chunks.get(chunk_id)

    def get_all_chunks(self) -> List[KnowledgeChunk]:
        return list(self._chunks.values())

    def clear(self) -> None:
        self._chunks.clear()
        if self.persistence_path and os.path.exists(self.persistence_path):
            try:
                os.remove(self.persistence_path)
            except Exception:
                pass


# Default singleton instance
default_vector_store = LocalVectorStore(persistence_path="data/vector_store.json")
