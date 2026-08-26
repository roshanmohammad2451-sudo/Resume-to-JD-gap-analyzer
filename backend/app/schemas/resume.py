from pydantic import BaseModel, Field
from typing import List, Optional


class ResumeSkill(BaseModel):
    name: str = Field(..., description="Canonical or extracted skill/technology name")
    evidence: str = Field(
        ..., 
        description="Exact supporting quote or clear textual evidence from the actual resume where this skill was mentioned or demonstrated."
    )
    source_section: str = Field(
        ..., 
        description="Section of the resume where evidence was found (e.g. 'Skills', 'Experience', 'Projects', 'Education')"
    )
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Confidence score from 0.0 to 1.0 based on explicit grounded evidence in the text"
    )


class ResumeEducation(BaseModel):
    degree: Optional[str] = Field(None, description="Degree or qualification name (e.g. Bachelor of Science in Computer Science)")
    institution: Optional[str] = Field(None, description="University, college, or educational institution name")
    dates: Optional[str] = Field(None, description="Years or graduation date range")
    details: Optional[str] = Field(None, description="Additional academic achievements, GPA, or honors")


class ResumeExperience(BaseModel):
    title: Optional[str] = Field(None, description="Job title or position held")
    company: Optional[str] = Field(None, description="Company or organization name")
    dates: Optional[str] = Field(None, description="Employment date range")
    responsibilities: List[str] = Field(
        default_factory=list, 
        description="List of key responsibilities, bullet points, and achievements"
    )


class ResumeProject(BaseModel):
    name: Optional[str] = Field(None, description="Project name or title")
    description: Optional[str] = Field(None, description="Summary description of the project and its goals")
    technologies: List[str] = Field(
        default_factory=list, 
        description="Explicitly mentioned technologies used in this project"
    )


class ResumeCertification(BaseModel):
    name: Optional[str] = Field(None, description="Name of certification or license")
    issuer: Optional[str] = Field(None, description="Issuing body or provider (e.g. AWS, Coursera, Microsoft)")
    date: Optional[str] = Field(None, description="Date or year issued/valid")


class ResumeProfile(BaseModel):
    name: Optional[str] = Field(None, description="Candidate's full name if explicitly stated in text")
    headline: Optional[str] = Field(None, description="Professional summary or title headline")
    education: List[ResumeEducation] = Field(
        default_factory=list, 
        description="List of verified educational background items"
    )
    experience: List[ResumeExperience] = Field(
        default_factory=list, 
        description="List of verified work experience items"
    )
    projects: List[ResumeProject] = Field(
        default_factory=list, 
        description="List of verified candidate projects"
    )
    certifications: List[ResumeCertification] = Field(
        default_factory=list, 
        description="List of verified candidate certifications"
    )
    skills: List[ResumeSkill] = Field(
        default_factory=list, 
        description="List of grounded, evidence-backed candidate skills"
    )


class ResumeAnalyzeRequest(BaseModel):
    text: str = Field(
        ..., 
        min_length=1, 
        description="Extracted raw text of candidate resume to analyze"
    )
