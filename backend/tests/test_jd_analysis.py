import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.jd import (
    JobDescription,
    JobSkill,
    JDAnalyzeRequest,
)
from app.services.llm_service import (
    LLMService,
    LLMKeyMissingError,
    LLMAPIError,
    LLMParseError,
)
from app.services.jd_parser import JDParserService

client = TestClient(app)


# Sample Mock Job Description Profiles
SAMPLE_NORMAL_JD_PROFILE = JobDescription(
    role="Senior Backend Engineer",
    company="Acme Corp",
    summary="We are looking for a Senior Backend Engineer to build scalable microservices.",
    required_skills=[
        JobSkill(
            name="Python",
            evidence="Must have 5+ years of experience with Python.",
            importance="required",
            source_text="Must have 5+ years of experience with Python."
        ),
        JobSkill(
            name="FastAPI",
            evidence="Strong proficiency in FastAPI or Django required.",
            importance="required",
            source_text="Strong proficiency in FastAPI or Django required."
        ),
        JobSkill(
            name="PostgreSQL",
            evidence="Experience designing relational schemas in PostgreSQL.",
            importance="required",
            source_text="Experience designing relational schemas in PostgreSQL."
        )
    ],
    preferred_skills=[
        JobSkill(
            name="Docker",
            evidence="Experience with Docker and Kubernetes is a plus.",
            importance="preferred",
            source_text="Experience with Docker and Kubernetes is a plus."
        ),
        JobSkill(
            name="Kubernetes",
            evidence="Experience with Docker and Kubernetes is a plus.",
            importance="preferred",
            source_text="Experience with Docker and Kubernetes is a plus."
        )
    ],
    responsibilities=[
        "Architect and maintain high-volume RESTful APIs.",
        "Collaborate with frontend engineers and product managers."
    ],
    qualifications=[
        "5+ years of software engineering experience.",
        "Bachelor's degree in Computer Science or equivalent experience."
    ]
)


# Test 1: Normal Technical JD Analysis Endpoint (Mocked LLM)
@pytest.mark.asyncio
async def test_analyze_normal_jd_endpoint():
    raw_jd_text = """
    Acme Corp - Senior Backend Engineer
    
    Summary:
    We are looking for a Senior Backend Engineer to build scalable microservices.

    Requirements:
    - Must have 5+ years of experience with Python.
    - Strong proficiency in FastAPI or Django required.
    - Experience designing relational schemas in PostgreSQL.

    Nice to Have:
    - Experience with Docker and Kubernetes is a plus.

    Responsibilities:
    - Architect and maintain high-volume RESTful APIs.
    - Collaborate with frontend engineers and product managers.
    """

    with patch("app.api.jd.default_jd_parser.analyze_jd_text", new_callable=AsyncMock) as mock_analyze:
        mock_analyze.return_value = SAMPLE_NORMAL_JD_PROFILE

        response = client.post(
            "/api/jd/analyze",
            json={"text": raw_jd_text}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "Senior Backend Engineer"
        assert data["company"] == "Acme Corp"
        assert len(data["required_skills"]) == 3
        assert data["required_skills"][0]["name"] == "Python"
        assert data["required_skills"][0]["importance"] == "required"
        assert len(data["preferred_skills"]) == 2
        assert data["preferred_skills"][0]["importance"] == "preferred"


# Test 2: JD with Explicit Required and Preferred Skills Distinction
@pytest.mark.asyncio
async def test_jd_required_vs_preferred_skills_distinction():
    jd_text = """
    Role: Frontend Developer
    Must Have Skills: React, TypeScript, CSS Modules
    Bonus Skills: Next.js, GraphQL
    """

    distinction_profile = JobDescription(
        role="Frontend Developer",
        required_skills=[
            JobSkill(
                name="React",
                evidence="Must Have Skills: React, TypeScript, CSS Modules",
                importance="required",
                source_text="Must Have Skills: React, TypeScript, CSS Modules"
            ),
            JobSkill(
                name="TypeScript",
                evidence="Must Have Skills: React, TypeScript, CSS Modules",
                importance="required",
                source_text="Must Have Skills: React, TypeScript, CSS Modules"
            )
        ],
        preferred_skills=[
            JobSkill(
                name="Next.js",
                evidence="Bonus Skills: Next.js, GraphQL",
                importance="preferred",
                source_text="Bonus Skills: Next.js, GraphQL"
            )
        ]
    )

    mock_llm = AsyncMock()
    mock_llm.generate_structured_output.return_value = distinction_profile

    parser = JDParserService(llm_service=mock_llm)
    result = await parser.analyze_jd_text(jd_text)

    assert result.role == "Frontend Developer"
    assert len(result.required_skills) == 2
    assert all(s.importance == "required" for s in result.required_skills)
    assert len(result.preferred_skills) == 1
    assert result.preferred_skills[0].importance == "preferred"


# Test 3: JD with No Explicit Skill Section Heading
@pytest.mark.asyncio
async def test_jd_with_no_explicit_skill_section():
    narrative_jd_text = """
    Data Platform Engineer at DataWorks
    You will develop ETL pipelines using Apache Spark and SQL to process terabytes of data daily.
    """

    narrative_profile = JobDescription(
        role="Data Platform Engineer",
        company="DataWorks",
        required_skills=[
            JobSkill(
                name="Apache Spark",
                evidence="develop ETL pipelines using Apache Spark and SQL",
                importance="required",
                source_text="You will develop ETL pipelines using Apache Spark and SQL to process terabytes of data daily."
            ),
            JobSkill(
                name="SQL",
                evidence="develop ETL pipelines using Apache Spark and SQL",
                importance="required",
                source_text="You will develop ETL pipelines using Apache Spark and SQL to process terabytes of data daily."
            )
        ]
    )

    mock_llm = AsyncMock()
    mock_llm.generate_structured_output.return_value = narrative_profile

    parser = JDParserService(llm_service=mock_llm)
    result = await parser.analyze_jd_text(narrative_jd_text)

    assert result.role == "Data Platform Engineer"
    assert len(result.required_skills) == 2
    assert result.required_skills[0].name == "Apache Spark"


# Test 4: Ambiguous Requirements Handling & Grounding Rules
@pytest.mark.asyncio
async def test_ambiguous_requirements_grounding():
    ambiguous_jd_text = """
    Software Developer position.
    Candidate will interact with teams using legacy systems.
    Must have hands-on experience building web apps with Java.
    Awareness of cloud technologies is helpful.
    """

    grounded_jd_profile = JobDescription(
        role="Software Developer",
        required_skills=[
            JobSkill(
                name="Java",
                evidence="Must have hands-on experience building web apps with Java.",
                importance="required",
                source_text="Must have hands-on experience building web apps with Java."
            )
        ],
        preferred_skills=[
            JobSkill(
                name="Cloud",
                evidence="Awareness of cloud technologies is helpful.",
                importance="preferred",
                source_text="Awareness of cloud technologies is helpful."
            )
        ]
    )

    mock_llm = AsyncMock()
    mock_llm.generate_structured_output.return_value = grounded_jd_profile

    parser = JDParserService(llm_service=mock_llm)
    result = await parser.analyze_jd_text(ambiguous_jd_text)

    req_names = [s.name for s in result.required_skills]
    assert "Java" in req_names
    # Ensure legacy systems was NOT converted into a required tech skill
    assert "legacy systems" not in req_names


# Test 5: Malformed AI Output Exception Handling
@pytest.mark.asyncio
async def test_malformed_ai_output_jd():
    mock_llm = AsyncMock()
    mock_llm.generate_structured_output.side_effect = LLMParseError("JD Validation failed")

    parser = JDParserService(llm_service=mock_llm)
    with pytest.raises(LLMParseError) as exc_info:
        await parser.analyze_jd_text("Valid JD content")

    assert "JD Validation failed" in str(exc_info.value)


# Test 6: Empty Text Validation
def test_empty_jd_text_api():
    response = client.post(
        "/api/jd/analyze",
        json={"text": "   "}
    )
    assert response.status_code == 422 or response.status_code == 400


@pytest.mark.asyncio
async def test_empty_jd_text_service():
    parser = JDParserService(llm_service=AsyncMock())
    with pytest.raises(ValueError) as exc_info:
        await parser.analyze_jd_text("   \n ")
    assert "cannot be empty" in str(exc_info.value)


# Test 7: API Status Code Error Mappings
def test_api_missing_key_status_code_jd():
    with patch("app.api.jd.default_jd_parser.analyze_jd_text", side_effect=LLMKeyMissingError("Missing key")):
        response = client.post(
            "/api/jd/analyze",
            json={"text": "Senior Developer Job Description"}
        )
        assert response.status_code == 500
        assert "OpenAI API key is missing" in response.json()["detail"]


def test_api_openai_api_error_status_code_jd():
    with patch("app.api.jd.default_jd_parser.analyze_jd_text", side_effect=LLMAPIError("API Timeout")):
        response = client.post(
            "/api/jd/analyze",
            json={"text": "Senior Developer Job Description"}
        )
        assert response.status_code == 502
        assert "OpenAI service communication error" in response.json()["detail"]
