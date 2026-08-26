import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.resume import (
    ResumeProfile,
    ResumeSkill,
    ResumeEducation,
    ResumeExperience,
    ResumeProject,
    ResumeCertification,
    ResumeAnalyzeRequest,
)
from app.services.llm_service import (
    LLMService,
    LLMKeyMissingError,
    LLMAPIError,
    LLMParseError,
)
from app.services.resume_analyzer import ResumeAnalyzerService

client = TestClient(app)


# Sample Mock Profiles
SAMPLE_NORMAL_PROFILE = ResumeProfile(
    name="Jane Doe",
    headline="Senior Software Engineer",
    education=[
        ResumeEducation(
            degree="Bachelor of Science in Computer Science",
            institution="Stanford University",
            dates="2016-2020",
            details="GPA 3.9"
        )
    ],
    experience=[
        ResumeExperience(
            title="Software Engineer",
            company="Tech Corp",
            dates="2020-Present",
            responsibilities=[
                "Built microservices using Python and FastAPI.",
                "Managed PostgreSQL databases and Redis caching."
            ]
        )
    ],
    projects=[
        ResumeProject(
            name="Analytics Platform",
            description="Built real-time dashboard using React and Tailwind CSS",
            technologies=["React", "Tailwind CSS", "TypeScript"]
        )
    ],
    certifications=[
        ResumeCertification(
            name="AWS Certified Solutions Architect",
            issuer="Amazon Web Services",
            date="2022"
        )
    ],
    skills=[
        ResumeSkill(
            name="Python",
            evidence="Built microservices using Python and FastAPI.",
            source_section="Experience",
            confidence=1.0
        ),
        ResumeSkill(
            name="FastAPI",
            evidence="Built microservices using Python and FastAPI.",
            source_section="Experience",
            confidence=1.0
        ),
        ResumeSkill(
            name="React",
            evidence="Built real-time dashboard using React and Tailwind CSS",
            source_section="Projects",
            confidence=1.0
        )
    ]
)


# Test 1: Normal Resume Analysis via API Endpoint (Mocked LLM)
@pytest.mark.asyncio
async def test_analyze_normal_resume_endpoint():
    raw_resume_text = """
    Jane Doe
    Senior Software Engineer

    Education:
    Stanford University, B.S. Computer Science (2016-2020)

    Experience:
    Tech Corp - Software Engineer (2020-Present)
    - Built microservices using Python and FastAPI.
    - Managed PostgreSQL databases and Redis caching.

    Projects:
    Analytics Platform: Built real-time dashboard using React and Tailwind CSS.

    Certifications:
    AWS Certified Solutions Architect (2022)

    Skills:
    Python, FastAPI, React, PostgreSQL
    """

    with patch("app.api.resume.default_resume_analyzer.analyze_resume_text", new_callable=AsyncMock) as mock_analyze:
        mock_analyze.return_value = SAMPLE_NORMAL_PROFILE

        response = client.post(
            "/api/resume/analyze",
            json={"text": raw_resume_text}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Jane Doe"
        assert len(data["skills"]) == 3
        assert data["skills"][0]["name"] == "Python"
        assert data["skills"][0]["evidence"] == "Built microservices using Python and FastAPI."
        assert data["skills"][2]["source_section"] == "Projects"


# Test 2: Skills Mentioned Inside Projects
@pytest.mark.asyncio
async def test_skills_mentioned_inside_projects():
    project_resume_text = """
    John Smith
    Projects:
    - Smart Home IoT Hub: Implemented MQTT message broker in Go and deployed on Kubernetes.
    """
    
    project_profile = ResumeProfile(
        name="John Smith",
        headline=None,
        education=[],
        experience=[],
        projects=[
            ResumeProject(
                name="Smart Home IoT Hub",
                description="Implemented MQTT message broker in Go and deployed on Kubernetes.",
                technologies=["Go", "MQTT", "Kubernetes"]
            )
        ],
        certifications=[],
        skills=[
            ResumeSkill(
                name="Go",
                evidence="Implemented MQTT message broker in Go and deployed on Kubernetes.",
                source_section="Projects",
                confidence=1.0
            ),
            ResumeSkill(
                name="Kubernetes",
                evidence="Implemented MQTT message broker in Go and deployed on Kubernetes.",
                source_section="Projects",
                confidence=1.0
            )
        ]
    )

    mock_llm = AsyncMock()
    mock_llm.generate_structured_output.return_value = project_profile

    analyzer = ResumeAnalyzerService(llm_service=mock_llm)
    result = await analyzer.analyze_resume_text(project_resume_text)

    assert len(result.skills) == 2
    assert result.skills[0].name == "Go"
    assert result.skills[0].source_section == "Projects"
    assert "in Go" in result.skills[0].evidence


# Test 3: Resume with No Explicit Skills Section
@pytest.mark.asyncio
async def test_resume_with_no_skills_section():
    no_skills_section_text = """
    Alice Johnson
    Work Experience:
    Data Analyst at Acme Corp (2021-2023)
    Executed SQL queries and created charts using Tableau.
    """

    no_skills_profile = ResumeProfile(
        name="Alice Johnson",
        skills=[
            ResumeSkill(
                name="SQL",
                evidence="Executed SQL queries and created charts using Tableau.",
                source_section="Experience",
                confidence=0.95
            ),
            ResumeSkill(
                name="Tableau",
                evidence="Executed SQL queries and created charts using Tableau.",
                source_section="Experience",
                confidence=0.95
            )
        ]
    )

    mock_llm = AsyncMock()
    mock_llm.generate_structured_output.return_value = no_skills_profile

    analyzer = ResumeAnalyzerService(llm_service=mock_llm)
    result = await analyzer.analyze_resume_text(no_skills_section_text)

    assert result.name == "Alice Johnson"
    assert len(result.skills) == 2
    assert result.skills[0].name == "SQL"
    assert result.skills[0].source_section == "Experience"


# Test 4: Ambiguous Technology Mentions & Grounding Enforcements
@pytest.mark.asyncio
async def test_ambiguous_technology_mentions():
    ambiguous_resume_text = """
    Bob Developer
    Summary:
    Interested in learning Rust and AI engineering.
    Collaborated closely with DevOps team who managed Docker and AWS.
    Experience:
    Backend Developer - Wrote REST APIs in Node.js.
    """

    # Grounded model should ONLY extract Node.js, NOT Docker/AWS/Rust/AI engineering
    grounded_profile = ResumeProfile(
        name="Bob Developer",
        headline="Backend Developer",
        experience=[
            ResumeExperience(
                title="Backend Developer",
                company=None,
                dates=None,
                responsibilities=["Wrote REST APIs in Node.js."]
            )
        ],
        skills=[
            ResumeSkill(
                name="Node.js",
                evidence="Wrote REST APIs in Node.js.",
                source_section="Experience",
                confidence=1.0
            )
        ]
    )

    mock_llm = AsyncMock()
    mock_llm.generate_structured_output.return_value = grounded_profile

    analyzer = ResumeAnalyzerService(llm_service=mock_llm)
    result = await analyzer.analyze_resume_text(ambiguous_resume_text)

    extracted_skill_names = [s.name for s in result.skills]
    assert "Node.js" in extracted_skill_names
    assert "Rust" not in extracted_skill_names
    assert "Docker" not in extracted_skill_names
    assert "AWS" not in extracted_skill_names


# Test 5: Malformed AI Output Handling
@pytest.mark.asyncio
async def test_malformed_ai_output():
    mock_llm = AsyncMock()
    mock_llm.generate_structured_output.side_effect = LLMParseError("Response validation failed")

    analyzer = ResumeAnalyzerService(llm_service=mock_llm)
    
    with pytest.raises(LLMParseError) as exc_info:
        await analyzer.analyze_resume_text("Valid candidate text")
    
    assert "Response validation failed" in str(exc_info.value)


# Test 6: Empty Resume Text Validation
def test_empty_resume_text_api():
    response = client.post(
        "/api/resume/analyze",
        json={"text": "   "}
    )
    assert response.status_code == 422 or response.status_code == 400


@pytest.mark.asyncio
async def test_empty_resume_text_service():
    analyzer = ResumeAnalyzerService(llm_service=AsyncMock())
    with pytest.raises(ValueError) as exc_info:
        await analyzer.analyze_resume_text("  \n  ")
    assert "cannot be empty" in str(exc_info.value)


# Test 7: Missing API Key Error Handling
@pytest.mark.asyncio
async def test_missing_api_key_handling():
    llm_service = LLMService(api_key="")
    with pytest.raises(LLMKeyMissingError) as exc_info:
        await llm_service.generate_structured_output("prompt", "sys_prompt", ResumeProfile)
    
    assert "Gemini API key is missing" in str(exc_info.value)


# Test 8: API Endpoint Error Responses
def test_api_missing_key_status_code():
    with patch("app.api.resume.default_resume_analyzer.analyze_resume_text", side_effect=LLMKeyMissingError("Missing key")):
        response = client.post(
            "/api/resume/analyze",
            json={"text": "John Doe developer resume"}
        )
        assert response.status_code == 500
        assert "OpenAI API key is missing" in response.json()["detail"]


def test_api_openai_api_error_status_code():
    with patch("app.api.resume.default_resume_analyzer.analyze_resume_text", side_effect=LLMAPIError("Connection timeout")):
        response = client.post(
            "/api/resume/analyze",
            json={"text": "John Doe developer resume"}
        )
        assert response.status_code == 502
        assert "OpenAI service communication error" in response.json()["detail"]
