import logging
from typing import Optional

from app.schemas.jd import JobDescription
from app.services.llm_service import LLMService, default_llm_service

logger = logging.getLogger(__name__)

JD_PARSER_SYSTEM_PROMPT = """You are a strict, deterministic AI job description analysis engine.
Your task is to parse raw Job Description text and extract structured requirement data strictly adhering to the output schema.

CRITICAL GROUNDING & CLASSIFICATION RULES:
1. ONLY extract requirements, skills, and duties explicitly supported by text present in the supplied Job Description.
2. NEVER INVENT technologies, frameworks, tools, or qualifications.
3. NEVER assume a skill is required without direct textual evidence.
4. ACCURATELY DISTINGUISH REQUIRED vs PREFERRED SKILLS:
   - Mark `importance="required"` and include in `required_skills` ONLY if the skill is listed under sections like "Requirements", "Must Have", "Basic Qualifications", "Minimum Qualifications", or explicitly described as mandatory (e.g. "Must have experience with Python").
   - Mark `importance="preferred"` and include in `preferred_skills` if listed under sections like "Nice to Have", "Preferred Qualifications", "Bonus Skills", "Pluses", or phrased as optional (e.g. "Experience with Docker is a plus").
5. EVERY extracted skill MUST include exact supporting text in `evidence` and full sentence/context in `source_text`.
6. Extract key responsibilities into the `responsibilities` list.
7. Extract qualifications (degree, experience years, certifications) into the `qualifications` list.
8. OMIT any unsupported information. If a section is missing, return an empty list.
"""


class JDParserService:
    """Dedicated domain service for parsing and analyzing Job Descriptions."""

    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service or default_llm_service

    async def analyze_jd_text(self, text: str) -> JobDescription:
        """
        Validates input text and extracts structured JobDescription using LLM service with strict grounding rules.
        """
        if not text or not text.strip():
            raise ValueError("Job Description text cannot be empty.")

        user_prompt = f"""Extract structured job requirements from the following Job Description text:

--- BEGIN JOB DESCRIPTION TEXT ---
{text.strip()}
--- END JOB DESCRIPTION TEXT ---

Remember all grounding rules:
- No invented technologies or qualifications.
- Preserve exact supporting text for every skill.
- Strictly categorize skills into required vs preferred based on explicit text.
- Return structured result matching the schema.
"""

        parsed_jd = await self.llm_service.generate_structured_output(
            prompt=user_prompt,
            system_prompt=JD_PARSER_SYSTEM_PROMPT,
            response_model=JobDescription
        )

        return parsed_jd


# Singleton instance
default_jd_parser = JDParserService()
