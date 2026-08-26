import logging
from typing import Optional

from app.schemas.resume import ResumeProfile
from app.services.llm_service import LLMService, default_llm_service

logger = logging.getLogger(__name__)

RESUME_ANALYZER_SYSTEM_PROMPT = """You are a strict, deterministic AI resume analysis engine.
Your task is to parse raw candidate resume text and extract structured profile data strictly adhering to the output schema.

CRITICAL GROUNDING & VERIFICATION RULES:
1. ONLY extract information explicitly supported by text present in the resume.
2. NEVER INVENT skills, projects, work experience, education, or certifications.
3. NEVER INFER technology knowledge without explicit evidence. (e.g., if candidate states "worked alongside Python team", do NOT extract Python as a skill for the candidate unless candidate explicitly wrote they used Python).
4. NEVER turn an interest, aspirational statement, or third-party mention into a confirmed candidate skill.
5. EVERY extracted skill MUST have exact, supporting evidence in the `evidence` field, quoted directly or verbatim from the resume text.
6. Specify the exact `source_section` where the skill evidence was found (e.g., "Skills", "Experience", "Projects", "Education", "Certifications").
7. Assign a `confidence` float score between 0.0 and 1.0 (1.0 for explicit skills listed under a Skills section or explicitly used in job duties; lower if implied by context).
8. OMIT any unsupported information. If a section (e.g., certifications or projects) is missing in the resume text, return an empty list for that section.
"""


class ResumeAnalyzerService:
    """Dedicated domain service for analyzing resume text into structured ResumeProfile."""

    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service or default_llm_service

    async def analyze_resume_text(self, text: str) -> ResumeProfile:
        """
        Validates input text and extracts structured candidate profile using LLM service with strict grounding rules.
        """
        if not text or not text.strip():
            raise ValueError("Resume text cannot be empty.")

        user_prompt = f"""Extract structured information from the following candidate resume text:

--- BEGIN RESUME TEXT ---
{text.strip()}
--- END RESUME TEXT ---

Remember all grounding rules:
- No invented skills, projects, experience, or certifications.
- Every skill MUST include direct evidence from the resume text above.
- Extract skills found inside experience bullet points and project descriptions into the skills list as well.
- Return structured result matching the schema.
"""

        profile = await self.llm_service.generate_structured_output(
            prompt=user_prompt,
            system_prompt=RESUME_ANALYZER_SYSTEM_PROMPT,
            response_model=ResumeProfile
        )

        return profile


# Singleton instance
default_resume_analyzer = ResumeAnalyzerService()
