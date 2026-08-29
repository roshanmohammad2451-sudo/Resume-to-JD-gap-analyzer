from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from app.schemas.gap import GapAnalysisResponse


class GroundedRecommendation(BaseModel):
    skill: str = Field(
        ..., 
        description="Target skill or competency addressed by this recommendation"
    )
    priority: Literal["high", "medium", "low"] = Field(
        ..., 
        description="Priority derived deterministically from the gap classification (high=required missing, medium=partial/experience, low=preferred)"
    )
    recommendation: str = Field(
        ..., 
        description="Concrete, actionable learning action strictly grounded in retrieved evidence"
    )
    rationale: str = Field(
        ..., 
        description="Explanation grounded in retrieved knowledge explaining how this addresses the gap"
    )
    evidence: List[str] = Field(
        default_factory=list, 
        description="Verbatim or summarized evidence quotes from retrieved knowledge chunks"
    )
    source_ids: List[str] = Field(
        default_factory=list, 
        description="Stable identifiers of the knowledge base documents/chunks cited as evidence"
    )
    grounding_status: Literal["grounded", "insufficient_evidence", "rejected"] = Field(
        ..., 
        description="Deterministic grounding validation status"
    )
    confidence: float = Field(
        default=1.0, 
        ge=0.0, 
        le=1.0, 
        description="Retrieval relevance score or validator confidence"
    )
    validation_details: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Detailed verification report from the deterministic grounding validator"
    )


class RecommendationRequest(BaseModel):
    gap_analysis: GapAnalysisResponse = Field(
        ..., 
        description="Deterministic GapAnalysisResponse from Phase 5"
    )
    max_recommendations: Optional[int] = Field(
        default=6, 
        ge=1, 
        le=20, 
        description="Maximum number of recommendations to generate"
    )


class RecommendationResponse(BaseModel):
    recommendations: List[GroundedRecommendation] = Field(
        default_factory=list, 
        description="Validated grounded recommendations strictly passing deterministic checks"
    )
    insufficient_evidence_gaps: List[str] = Field(
        default_factory=list, 
        description="Identified gaps where retrieval found insufficient evidence to generate a safe recommendation"
    )
    rejected_recommendations: List[GroundedRecommendation] = Field(
        default_factory=list, 
        description="Generated items rejected by the deterministic grounding validator (excluded from primary display)"
    )
    summary: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Statistical summary of gaps, retrieval, and grounding validation results"
    )
