import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
import json
from unittest.mock import AsyncMock

from app.schemas.resume import ResumeProfile, ResumeSkill, ResumeExperience, ResumeProject, ResumeEducation
from app.services.resume_analyzer import ResumeAnalyzerService

sample_resume_text = """
Alex Rivera
Full Stack Engineer | Cloud Practitioner
Email: alex.rivera@example.com | San Francisco, CA

EDUCATION:
University of California, Berkeley — B.S. in Electrical Engineering & Computer Sciences (2017 - 2021)

WORK EXPERIENCE:
Senior Software Engineer | CloudScale Tech (2021 - Present)
- Designed and built high-throughput REST APIs using Python, FastAPI, and PostgreSQL.
- Decreased query latency by 45% by implementing Redis caching and database indexing.
- Containerized microservices using Docker and deployed workloads on AWS EKS (Kubernetes).

PROJECTS:
AI Document Summarizer
- Developed a web application leveraging OpenAI GPT-4 API and React to summarize length PDF documents.
- Built backend services in Python and deployed on Vercel.

SKILLS:
Languages: Python, JavaScript, TypeScript, SQL, Go
Frameworks: FastAPI, React, Node.js, Express
Tools & Cloud: Docker, Kubernetes, AWS, PostgreSQL, Redis, Git
"""

async def run_demo():
    print("=== Testing Real Resume Analysis Engine ===")
    
    # Create sample grounded profile output demonstration
    mock_profile = ResumeProfile(
        name="Alex Rivera",
        headline="Full Stack Engineer | Cloud Practitioner",
        education=[
            ResumeEducation(
                degree="B.S. in Electrical Engineering & Computer Sciences",
                institution="University of California, Berkeley",
                dates="2017 - 2021"
            )
        ],
        experience=[
            ResumeExperience(
                title="Senior Software Engineer",
                company="CloudScale Tech",
                dates="2021 - Present",
                responsibilities=[
                    "Designed and built high-throughput REST APIs using Python, FastAPI, and PostgreSQL.",
                    "Decreased query latency by 45% by implementing Redis caching and database indexing.",
                    "Containerized microservices using Docker and deployed workloads on AWS EKS (Kubernetes)."
                ]
            )
        ],
        projects=[
            ResumeProject(
                name="AI Document Summarizer",
                description="Developed a web application leveraging OpenAI GPT-4 API and React to summarize length PDF documents.",
                technologies=["OpenAI API", "React", "Python", "Vercel"]
            )
        ],
        certifications=[],
        skills=[
            ResumeSkill(
                name="Python",
                evidence="Designed and built high-throughput REST APIs using Python, FastAPI, and PostgreSQL.",
                source_section="Experience",
                confidence=1.0
            ),
            ResumeSkill(
                name="FastAPI",
                evidence="Designed and built high-throughput REST APIs using Python, FastAPI, and PostgreSQL.",
                source_section="Experience",
                confidence=1.0
            ),
            ResumeSkill(
                name="PostgreSQL",
                evidence="Designed and built high-throughput REST APIs using Python, FastAPI, and PostgreSQL.",
                source_section="Experience",
                confidence=1.0
            ),
            ResumeSkill(
                name="Docker",
                evidence="Containerized microservices using Docker and deployed workloads on AWS EKS (Kubernetes).",
                source_section="Experience",
                confidence=1.0
            ),
            ResumeSkill(
                name="Kubernetes",
                evidence="Containerized microservices using Docker and deployed workloads on AWS EKS (Kubernetes).",
                source_section="Experience",
                confidence=1.0
            ),
            ResumeSkill(
                name="React",
                evidence="Developed a web application leveraging OpenAI GPT-4 API and React to summarize length PDF documents.",
                source_section="Projects",
                confidence=1.0
            )
        ]
    )

    mock_llm = AsyncMock()
    mock_llm.generate_structured_output.return_value = mock_profile

    analyzer = ResumeAnalyzerService(llm_service=mock_llm)
    result = await analyzer.analyze_resume_text(sample_resume_text)

    json_output = result.model_dump_json(indent=2)
    print("\n--- RESULTING JSON OUTPUT ---")
    print(json_output)
    
    # Validation checks
    assert result.name == "Alex Rivera"
    assert len(result.skills) == 6
    for skill in result.skills:
        assert skill.evidence != ""
        assert skill.source_section in ["Skills", "Experience", "Projects", "Education"]
        assert 0.0 <= skill.confidence <= 1.0

    print("\n[OK] Validation passed successfully!")

if __name__ == "__main__":
    asyncio.run(run_demo())
