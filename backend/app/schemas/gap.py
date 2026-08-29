from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from app.schemas.resume import ResumeProfile
from app.schemas.jd import JobDescription


class SkillGapItem(BaseModel):
    normalized_skill_name: str = Field(
        ..., 
        description="Normalized canonical skill name used for deterministic comparison"
    )
    original_jd_wording: Optional[str] = Field(
        None, 
        description="Original skill name or requirement text as specified in the Job Description"
    )
    original_resume_wording: Optional[str] = Field(
        None, 
        description="Original skill name or phrase as stated in Candidate Resume if matched/partial"
    )
    category: Optional[str] = Field(
        None, 
        description="Skill category or context if available"
    )
    requirement_importance: Literal["required", "preferred"] = Field(
        ..., 
        description="Requirement classification strictly as 'required' or 'preferred'"
    )
    match_status: Literal["matched", "partial", "missing"] = Field(
        ..., 
        description="Deterministic match evaluation: 'matched', 'partial', or 'missing'"
    )
    evidence: Optional[str] = Field(
        None, 
        description="Combined explanation of supporting evidence"
    )
    jd_evidence: Optional[str] = Field(
        None, 
        description="Exact supporting quote or requirement context from Job Description"
    )
    resume_evidence: Optional[str] = Field(
        None, 
        description="Exact supporting quote or section evidence from candidate Resume if matched/partial"
    )


class ExperienceGapItem(BaseModel):
    requirement: str = Field(
        ..., 
        description="Job responsibility or experience requirement from Job Description"
    )
    resume_evidence: Optional[str] = Field(
        None, 
        description="Relevant experience or bullet point found in candidate resume"
    )
    status: Literal["matched", "partial", "missing"] = Field(
        ..., 
        description="Deterministic match status for job responsibility: 'matched', 'partial', or 'missing'"
    )
    details: Optional[str] = Field(
        None, 
        description="Explanation or reasoning for gap classification"
    )


class QualificationGapItem(BaseModel):
    requirement: str = Field(
        ..., 
        description="Education or qualification requirement from Job Description"
    )
    resume_evidence: Optional[str] = Field(
        None, 
        description="Matching education, certification, or qualification from candidate resume"
    )
    status: Literal["matched", "partial", "missing"] = Field(
        ..., 
        description="Deterministic match status for qualification requirement: 'matched', 'partial', or 'missing'"
    )
    details: Optional[str] = Field(
        None, 
        description="Explanation or reasoning for gap classification"
    )


class GapAnalysisRequest(BaseModel):
    resume_profile: ResumeProfile = Field(
        ..., 
        description="Structured candidate ResumeProfile object"
    )
    job_description: JobDescription = Field(
        ..., 
        description="Structured JobDescription requirement object"
    )


class GapAnalysisResponse(BaseModel):
    overall_match_score: float = Field(
        ..., 
        ge=0.0, 
        le=100.0, 
        description="Deterministic overall match score percentage (0.0 to 100.0)"
    )
    matched_skills: List[SkillGapItem] = Field(
        default_factory=list, 
        description="List of fully matched skills across required and preferred requirements"
    )
    partial_matches: List[SkillGapItem] = Field(
        default_factory=list, 
        description="List of partially matched skills across required and preferred requirements"
    )
    missing_required_skills: List[SkillGapItem] = Field(
        default_factory=list, 
        description="List of missing required skills"
    )
    missing_preferred_skills: List[SkillGapItem] = Field(
        default_factory=list, 
        description="List of missing preferred skills"
    )
    experience_gaps: List[ExperienceGapItem] = Field(
        default_factory=list, 
        description="Gap analysis comparing JD responsibilities against candidate experience"
    )
    qualification_gaps: List[QualificationGapItem] = Field(
        default_factory=list, 
        description="Gap analysis comparing JD qualifications against candidate education & certifications"
    )
    evidence: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Preserved textual evidence structured by skill and requirement status"
    )
    summary: Dict[str, Any] = Field(
        default_factory=dict, 
        description="High-level statistical summary of match scores and counts"
    )


# Alias for compatibility
GapAnalysis = GapAnalysisResponse
