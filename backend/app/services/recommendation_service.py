import logging
import re
from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.recommendation import GroundedRecommendation
from app.services.retrieval_service import RetrievedEvidence
from app.services.grounding_validator import DeterministicGroundingValidator, default_grounding_validator
from app.services.llm_service import LLMService, default_llm_service, LLMServiceError

logger = logging.getLogger(__name__)


class RawGeminiRecommendation(BaseModel):
    recommendation: str = Field(
        ..., 
        description="Concise, actionable learning recommendation based ONLY on retrieved evidence"
    )
    rationale: str = Field(
        ..., 
        description="Explanation referencing concepts in the retrieved evidence"
    )
    cited_concepts: List[str] = Field(
        default_factory=list, 
        description="Key concepts cited from the retrieved knowledge chunks"
    )
    cited_source_ids: List[str] = Field(
        default_factory=list, 
        description="List of source_ids from retrieved chunks referenced"
    )


class RecommendationService:
    """
    Service responsible for synthesizing grounded recommendations from retrieved knowledge chunks.
    Constrains Gemini to retrieved evidence only, and validates every generated output
    with the DeterministicGroundingValidator.
    """

    def __init__(
        self,
        llm_service: LLMService = default_llm_service,
        validator: DeterministicGroundingValidator = default_grounding_validator,
    ):
        self.llm_service = llm_service
        self.validator = validator

    def _synthesize_deterministic_grounded_recommendation(
        self,
        skill: str,
        priority: str,
        retrieved_evidence: List[RetrievedEvidence],
        jd_evidence: Optional[str] = None,
        resume_evidence: Optional[str] = None,
    ) -> GroundedRecommendation:
        """
        Deterministic synthesis directly extracting concepts and practice projects
        from the top retrieved knowledge chunks. Used in offline tests or fallback.
        """
        top_chunk = retrieved_evidence[0]
        source_ids = sorted(list({c.source_id for c in retrieved_evidence}))

        # Extract practice project or learning objective lines from the chunk text
        practice_lines = [
            line.strip().lstrip("-*# ") 
            for line in top_chunk.text.splitlines() 
            if any(k in line.lower() for k in ["project", "practice", "build", "create", "objective", "implement"])
            and len(line.strip()) > 15
        ]

        if practice_lines:
            primary_action = practice_lines[0]
        else:
            primary_action = f"Study core {top_chunk.title} concepts and apply them in a hands-on project."

        recommendation_text = f"Focus on {skill}: {primary_action}."
        rationale_text = (
            f"Based on curated knowledge document '{top_chunk.title}' ({top_chunk.source_id}), "
            f"mastering these {skill} concepts directly addresses the job requirement."
        )

        validation = self.validator.validate_recommendation(
            skill=skill,
            recommendation_text=recommendation_text,
            rationale_text=rationale_text,
            retrieved_evidence=retrieved_evidence,
            cited_source_ids=source_ids,
        )

        return GroundedRecommendation(
            skill=skill,
            priority=priority,  # type: ignore[arg-type]
            recommendation=recommendation_text,
            rationale=rationale_text,
            evidence=[c.text[:200] + "..." if len(c.text) > 200 else c.text for c in retrieved_evidence[:2]],
            source_ids=source_ids,
            grounding_status="grounded" if validation.is_grounded else "rejected",
            confidence=validation.confidence,
            validation_details=validation.to_dict(),
        )

    async def generate_recommendation(
        self,
        skill: str,
        priority: str,
        retrieved_evidence: List[RetrievedEvidence],
        jd_evidence: Optional[str] = None,
        resume_evidence: Optional[str] = None,
    ) -> GroundedRecommendation:
        """
        Generates a grounded recommendation for a single skill gap using retrieved evidence.
        """
        source_ids = sorted(list({c.source_id for c in retrieved_evidence}))

        if not retrieved_evidence:
            return GroundedRecommendation(
                skill=skill,
                priority=priority,  # type: ignore[arg-type]
                recommendation="Insufficient grounded evidence to generate a recommendation for this gap.",
                rationale="The local curated knowledge base does not contain verified reference material for this skill.",
                evidence=[],
                source_ids=[],
                grounding_status="insufficient_evidence",
                confidence=0.0,
                validation_details={"status": "insufficient_evidence", "is_grounded": False},
            )

        # Prepare constrained context for Gemini
        context_blocks = []
        for i, chunk in enumerate(retrieved_evidence, 1):
            context_blocks.append(
                f"[Document {i} | Source ID: {chunk.source_id} | Title: {chunk.title} | Section: {chunk.section}]\n{chunk.text}"
            )
        retrieved_context_str = "\n\n".join(context_blocks)

        system_prompt = (
            "You are a strict deterministic career coach and technical tutor for the Resume-to-JD Gap Analyzer.\n"
            "CRITICAL ANTI-HALLUCINATION RULES:\n"
            "1. Use ONLY the provided Retrieved Knowledge Chunks below. Do NOT use outside knowledge.\n"
            "2. Do NOT invent or mention external platforms (e.g. Coursera, Udemy, edX, YouTube, etc.).\n"
            "3. Do NOT invent URLs, links, or specific third-party courses.\n"
            "4. Do NOT introduce unrelated programming languages or tools absent from the chunks.\n"
            "5. Synthesize a practical learning recommendation directly referencing concepts and practice ideas in the chunks.\n"
            "6. Every claim MUST be supported by the provided text. Keep it concise, professional, and actionable."
        )

        user_prompt = (
            f"TARGET SKILL GAP: {skill}\n"
            f"GAP PRIORITY: {priority}\n"
            f"JD REQUIREMENT CONTEXT: {jd_evidence or 'Required in Job Description'}\n"
            f"CANDIDATE RESUME EVIDENCE: {resume_evidence or 'Not found in candidate resume'}\n\n"
            f"=== RETRIEVED KNOWLEDGE CHUNKS (ONLY SOURCE OF TRUTH) ===\n"
            f"{retrieved_context_str}\n\n"
            "Generate a structured grounded recommendation citing concepts and source_ids strictly from the chunks above."
        )

        try:
            raw_output: RawGeminiRecommendation = await self.llm_service.generate_structured_output(
                prompt=user_prompt,
                system_prompt=system_prompt,
                response_model=RawGeminiRecommendation,
            )

            # Pass through the Deterministic Grounding Validator
            validation = self.validator.validate_recommendation(
                skill=skill,
                recommendation_text=raw_output.recommendation,
                rationale_text=raw_output.rationale,
                retrieved_evidence=retrieved_evidence,
                cited_source_ids=raw_output.cited_source_ids or source_ids,
            )

            if validation.is_grounded:
                return GroundedRecommendation(
                    skill=skill,
                    priority=priority,  # type: ignore[arg-type]
                    recommendation=raw_output.recommendation,
                    rationale=raw_output.rationale,
                    evidence=[c.text[:200] + "..." if len(c.text) > 200 else c.text for c in retrieved_evidence[:2]],
                    source_ids=raw_output.cited_source_ids or source_ids,
                    grounding_status="grounded",
                    confidence=validation.confidence,
                    validation_details=validation.to_dict(),
                )
            else:
                logger.warning(
                    "Generated recommendation for '%s' was rejected by grounding validator: %s",
                    skill, validation.reasons
                )
                # Fallback to deterministic synthesis strictly from chunk text
                fallback_rec = self._synthesize_deterministic_grounded_recommendation(
                    skill=skill,
                    priority=priority,
                    retrieved_evidence=retrieved_evidence,
                    jd_evidence=jd_evidence,
                    resume_evidence=resume_evidence,
                )
                fallback_rec.validation_details["note"] = "Regenerated via deterministic template after validator rejection."
                return fallback_rec

        except LLMServiceError as e:
            logger.info("LLM service unavailable or key missing (%s). Using deterministic grounded synthesis.", str(e))
            return self._synthesize_deterministic_grounded_recommendation(
                skill=skill,
                priority=priority,
                retrieved_evidence=retrieved_evidence,
                jd_evidence=jd_evidence,
                resume_evidence=resume_evidence,
            )


default_recommendation_service = RecommendationService()
