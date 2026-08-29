import logging
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

from app.services.vector_store import BaseVectorStore, KnowledgeChunk, default_vector_store
from app.services.embedding_service import EmbeddingService, default_embedding_service
from app.services.gap_engine import normalize_skill_name
from app.core.config import settings

logger = logging.getLogger(__name__)


class RetrievedEvidence(BaseModel):
    chunk_id: str
    source_id: str
    title: str
    section: Optional[str] = None
    text: str
    similarity: float


class SkillRetrievalResult(BaseModel):
    skill: str
    normalized_skill: str
    status: Literal["sufficient", "insufficient_evidence"]
    evidence_chunks: List[RetrievedEvidence] = Field(default_factory=list)
    source_ids: List[str] = Field(default_factory=list)
    top_similarity: float = 0.0
    details: Optional[str] = None


class RetrievalService:
    """
    Retrieval service executing semantic similarity search against the controlled knowledge base.
    Guarantees evidence-first retrieval: never fabricates chunks, respects minimum similarity
    thresholds, and rejects queries where insufficient grounded evidence is available.
    """

    def __init__(
        self,
        vector_store: BaseVectorStore = default_vector_store,
        embedding_service: EmbeddingService = default_embedding_service,
        top_k: int = settings.RETRIEVAL_TOP_K,
        min_similarity: float = settings.RETRIEVAL_MIN_SIMILARITY,
    ):
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.top_k = top_k
        self.min_similarity = min_similarity

    async def retrieve_for_skill(
        self,
        skill_name: str,
        top_k: Optional[int] = None,
        min_similarity: Optional[float] = None,
    ) -> SkillRetrievalResult:
        """
        Retrieves knowledge chunks for a missing or partial skill from GapAnalysis.
        """
        k = top_k if top_k is not None else self.top_k
        threshold = min_similarity if min_similarity is not None else self.min_similarity

        clean_name = skill_name.strip()
        norm_name = normalize_skill_name(clean_name)

        if not norm_name:
            return SkillRetrievalResult(
                skill=clean_name,
                normalized_skill="",
                status="insufficient_evidence",
                details="Empty skill name provided for retrieval.",
            )

        # 1. Semantic query generation
        query_text = f"Learning roadmap, core concepts, and practical projects for {clean_name} ({norm_name})"
        query_embedding = await self.embedding_service.get_embedding(query_text)

        # 2. Vector search: first try matching the specific skill in metadata
        search_results = await self.vector_store.search(
            query_embedding=query_embedding,
            top_k=k,
            filter_skill=norm_name,
            min_similarity=threshold,
        )

        # If not enough chunks with exact skill filter, broaden search to all chunks
        if len(search_results) == 0:
            search_results = await self.vector_store.search(
                query_embedding=query_embedding,
                top_k=k,
                filter_skill=None,
                min_similarity=threshold,
            )

        # 3. Filter by similarity threshold
        passing_results = [r for r in search_results if r.similarity >= threshold]

        if not passing_results:
            logger.info(
                "Insufficient evidence for skill '%s' (norm: '%s'). Top similarity was below threshold %.2f.",
                clean_name, norm_name, threshold
            )
            return SkillRetrievalResult(
                skill=clean_name,
                normalized_skill=norm_name,
                status="insufficient_evidence",
                evidence_chunks=[],
                source_ids=[],
                top_similarity=search_results[0].similarity if search_results else 0.0,
                details=f"No curated knowledge chunks reached minimum similarity threshold of {threshold:.2f}."
            )

        evidence_chunks: List[RetrievedEvidence] = []
        source_ids_set = set()

        for res in passing_results:
            chunk = res.chunk
            source_ids_set.add(chunk.source_id)
            evidence_chunks.append(
                RetrievedEvidence(
                    chunk_id=chunk.chunk_id,
                    source_id=chunk.source_id,
                    title=chunk.title,
                    section=chunk.section,
                    text=chunk.text,
                    similarity=res.similarity,
                )
            )

        top_sim = passing_results[0].similarity

        return SkillRetrievalResult(
            skill=clean_name,
            normalized_skill=norm_name,
            status="sufficient",
            evidence_chunks=evidence_chunks,
            source_ids=sorted(list(source_ids_set)),
            top_similarity=top_sim,
            details=f"Retrieved {len(evidence_chunks)} grounded chunks from knowledge base."
        )


default_retrieval_service = RetrievalService()
