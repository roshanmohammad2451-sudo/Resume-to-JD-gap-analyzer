import logging
from typing import List, Tuple
from fastapi import APIRouter, HTTPException, status

from app.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    GroundedRecommendation,
)
from app.schemas.gap import SkillGapItem
from app.services.retrieval_service import RetrievalService, default_retrieval_service
from app.services.recommendation_service import RecommendationService, default_recommendation_service
from app.services.knowledge_service import default_knowledge_service
from app.services.vector_store import default_vector_store

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/recommendations/analyze",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Grounded Learning Recommendations from Curated Knowledge",
    description=(
        "Retrieves verified knowledge chunks for missing and partial skills from the deterministic gap analysis, "
        "synthesizes grounded recommendations, and strictly verifies output through the deterministic grounding validator."
    ),
)
async def analyze_recommendations(
    request: RecommendationRequest,
) -> RecommendationResponse:
    gap_result = request.gap_analysis
    max_recs = request.max_recommendations or 6

    # Ensure vector store is initialized with curated knowledge base
    if len(default_vector_store.get_all_chunks()) == 0:
        logger.info("Vector store empty on recommendation request. Running knowledge ingestion...")
        await default_knowledge_service.ingest_all()

    # 1. Collect candidate gaps in strict priority order:
    # High priority: Missing required skills
    # Medium priority: Partially matched skills
    # Low priority: Missing preferred skills
    gap_candidates: List[Tuple[SkillGapItem, str]] = []

    for item in gap_result.missing_required_skills:
        gap_candidates.append((item, "high"))

    for item in gap_result.partial_matches:
        gap_candidates.append((item, "medium"))

    for item in gap_result.missing_preferred_skills:
        gap_candidates.append((item, "low"))

    recommendations: List[GroundedRecommendation] = []
    insufficient_gaps: List[str] = []
    rejected_recs: List[GroundedRecommendation] = []

    seen_skills = set()

    for item, priority in gap_candidates:
        if len(recommendations) >= max_recs:
            break

        norm_name = item.normalized_skill_name.lower().strip()
        if norm_name in seen_skills:
            continue
        seen_skills.add(norm_name)

        # 2. Retrieve grounded evidence from knowledge base
        retrieval_res = await default_retrieval_service.retrieve_for_skill(item.normalized_skill_name)

        if retrieval_res.status != "sufficient" or not retrieval_res.evidence_chunks:
            insufficient_gaps.append(item.normalized_skill_name)
            # Create a transparent "insufficient evidence" record for full traceability
            no_hallucination_rec = GroundedRecommendation(
                skill=item.normalized_skill_name,
                priority=priority,  # type: ignore[arg-type]
                recommendation=f"No verified curriculum available in curated knowledge base for '{item.normalized_skill_name}'.",
                rationale="The system refuses to hallucinate external learning materials without grounded source evidence.",
                evidence=[],
                source_ids=[],
                grounding_status="insufficient_evidence",
                confidence=0.0,
                validation_details={
                    "status": "insufficient_evidence",
                    "reason": "Top retrieval similarity below threshold. Zero hallucination guarantee active.",
                },
            )
            recommendations.append(no_hallucination_rec)
            continue

        # 3. Synthesize recommendation strictly from retrieved evidence
        rec = await default_recommendation_service.generate_recommendation(
            skill=item.normalized_skill_name,
            priority=priority,
            retrieved_evidence=retrieval_res.evidence_chunks,
            jd_evidence=item.jd_evidence,
            resume_evidence=item.resume_evidence,
        )

        if rec.grounding_status == "grounded":
            recommendations.append(rec)
        elif rec.grounding_status == "insufficient_evidence":
            insufficient_gaps.append(item.normalized_skill_name)
            recommendations.append(rec)
        else:
            rejected_recs.append(rec)
            insufficient_gaps.append(item.normalized_skill_name)

    summary_stats = {
        "total_gaps_evaluated": len(seen_skills),
        "grounded_recommendations_count": sum(1 for r in recommendations if r.grounding_status == "grounded"),
        "insufficient_evidence_gaps_count": len(insufficient_gaps),
        "rejected_count": len(rejected_recs),
        "knowledge_base_chunks_active": len(default_vector_store.get_all_chunks()),
        "anti_hallucination_guarantee": "All verified recommendations are 100% grounded in retrieved local KB evidence.",
    }

    return RecommendationResponse(
        recommendations=recommendations,
        insufficient_evidence_gaps=insufficient_gaps,
        rejected_recommendations=rejected_recs,
        summary=summary_stats,
    )
