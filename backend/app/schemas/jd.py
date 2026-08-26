from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class JobSkill(BaseModel):
    name: str = Field(..., description="Canonical or extracted skill/technology name")
    evidence: str = Field(
        ..., 
        description="Exact supporting quote or clear textual evidence from the job description."
    )
    importance: Literal["required", "preferred"] = Field(
        ..., 
        description="Classification of skill importance strictly as 'required' or 'preferred'."
    )
    source_text: str = Field(
        ..., 
        description="Original context or sentence from the job description where the skill requirement was specified."
    )


class JobDescription(BaseModel):
    role: Optional[str] = Field(None, description="Job title or target role name (e.g. Senior Backend Engineer)")
    company: Optional[str] = Field(None, description="Company or hiring organization name if explicitly specified")
    summary: Optional[str] = Field(None, description="High-level overview of the job role and department")
    required_skills: List[JobSkill] = Field(
        default_factory=list, 
        description="List of mandatory, required skills extracted from the job description"
    )
    preferred_skills: List[JobSkill] = Field(
        default_factory=list, 
        description="List of nice-to-have, preferred skills extracted from the job description"
    )
    responsibilities: List[str] = Field(
        default_factory=list, 
        description="List of key duties, job responsibilities, and expected deliverables"
    )
    qualifications: List[str] = Field(
        default_factory=list, 
        description="List of education, experience, or credential requirements (e.g. 5+ years experience, B.S. in CS)"
    )


class JDAnalyzeRequest(BaseModel):
    text: str = Field(
        ..., 
        min_length=1, 
        description="Raw job description text to parse and analyze"
    )
