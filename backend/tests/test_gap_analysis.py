import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.resume import ResumeProfile, ResumeSkill, ResumeExperience, ResumeEducation
from app.schemas.jd import JobDescription, JobSkill
from app.schemas.gap import GapAnalysisResponse
from app.services.gap_engine import default_gap_engine, normalize_skill_name

client = TestClient(app)


def test_skill_normalization():
    assert normalize_skill_name("MS Excel") == "excel"
    assert normalize_skill_name("Microsoft Excel") == "excel"
    assert normalize_skill_name("Power BI") == "power bi"
    assert normalize_skill_name("Python programming") == "python"
    assert normalize_skill_name("Pandas library") == "pandas"
    assert normalize_skill_name("React.js") == "react"


def test_exact_skill_match():
    resume = ResumeProfile(
        skills=[
            ResumeSkill(
                name="Python",
                evidence="3 years Python backend development",
                source_section="Skills",
                confidence=1.0
            )
        ]
    )
    jd = JobDescription(
        required_skills=[
            JobSkill(
                name="Python",
                evidence="Must have Python programming experience",
                importance="required",
                source_text="Must have Python programming experience"
            )
        ]
    )

    result = default_gap_engine.analyze_gap(resume, jd)
    assert len(result.matched_skills) == 1
    assert result.matched_skills[0].normalized_skill_name == "python"
    assert result.matched_skills[0].match_status == "matched"
    assert result.overall_match_score == 100.0


def test_normalized_skill_match():
    resume = ResumeProfile(
        skills=[
            ResumeSkill(
                name="Microsoft Excel",
                evidence="Advanced Microsoft Excel financial modeling",
                source_section="Skills",
                confidence=0.9
            ),
            ResumeSkill(
                name="Pandas library",
                evidence="Used Pandas library for data analysis",
                source_section="Skills",
                confidence=0.95
            )
        ]
    )
    jd = JobDescription(
        required_skills=[
            JobSkill(
                name="MS Excel",
                evidence="Proficiency in MS Excel required",
                importance="required",
                source_text="Proficiency in MS Excel required"
            ),
            JobSkill(
                name="Pandas",
                evidence="Experience with Pandas for data manipulation",
                importance="required",
                source_text="Experience with Pandas for data manipulation"
            )
        ]
    )

    result = default_gap_engine.analyze_gap(resume, jd)
    assert len(result.matched_skills) == 2
    matched_names = {item.normalized_skill_name for item in result.matched_skills}
    assert matched_names == {"excel", "pandas"}
    assert result.overall_match_score == 100.0


def test_missing_required_skill():
    resume = ResumeProfile(
        skills=[
            ResumeSkill(
                name="Python",
                evidence="Python scripts",
                source_section="Skills",
                confidence=1.0
            )
        ]
    )
    jd = JobDescription(
        required_skills=[
            JobSkill(
                name="Python",
                evidence="Python required",
                importance="required",
                source_text="Python required"
            ),
            JobSkill(
                name="Docker",
                evidence="Docker containerization required",
                importance="required",
                source_text="Docker containerization required"
            )
        ]
    )

    result = default_gap_engine.analyze_gap(resume, jd)
    assert len(result.matched_skills) == 1
    assert len(result.missing_required_skills) == 1
    assert result.missing_required_skills[0].normalized_skill_name == "docker"
    # Required skills score: (1.0 + 0.0) / 2 = 0.5 -> 50.0%
    assert result.overall_match_score == 50.0


def test_missing_preferred_skill():
    resume = ResumeProfile(
        skills=[
            ResumeSkill(
                name="Python",
                evidence="Python dev",
                source_section="Skills",
                confidence=1.0
            )
        ]
    )
    jd = JobDescription(
        required_skills=[
            JobSkill(
                name="Python",
                evidence="Python required",
                importance="required",
                source_text="Python required"
            )
        ],
        preferred_skills=[
            JobSkill(
                name="Kubernetes",
                evidence="Kubernetes is a plus",
                importance="preferred",
                source_text="Kubernetes is a plus"
            )
        ]
    )

    result = default_gap_engine.analyze_gap(resume, jd)
    assert len(result.matched_skills) == 1
    assert len(result.missing_preferred_skills) == 1
    assert result.missing_preferred_skills[0].normalized_skill_name == "kubernetes"
    # Score: Required avg = 1.0 (70%), Preferred avg = 0.0 (30%) -> Overall = 70.0%
    assert result.overall_match_score == 70.0


def test_partial_skill_match():
    resume = ResumeProfile(
        skills=[
            ResumeSkill(
                name="React Native",
                evidence="Mobile app dev using React Native",
                source_section="Projects",
                confidence=0.8
            )
        ]
    )
    jd = JobDescription(
        required_skills=[
            JobSkill(
                name="React.js",
                evidence="Frontend with React.js",
                importance="required",
                source_text="Frontend with React.js"
            )
        ]
    )

    result = default_gap_engine.analyze_gap(resume, jd)
    assert len(result.partial_matches) == 1
    assert result.partial_matches[0].match_status == "partial"
    assert result.partial_matches[0].normalized_skill_name == "react"
    # Required skills score: 0.5 -> 50.0%
    assert result.overall_match_score == 50.0


def test_duplicate_skill_handling():
    resume = ResumeProfile(
        skills=[
            ResumeSkill(
                name="Python",
                evidence="Python experience 1",
                source_section="Skills",
                confidence=0.8
            ),
            ResumeSkill(
                name="Python programming",
                evidence="Python experience 2",
                source_section="Experience",
                confidence=1.0
            )
        ]
    )
    jd = JobDescription(
        required_skills=[
            JobSkill(
                name="Python",
                evidence="Must know Python",
                importance="required",
                source_text="Must know Python"
            ),
            JobSkill(
                name="Python programming",
                evidence="Python language experience",
                importance="required",
                source_text="Python language experience"
            )
        ],
        preferred_skills=[
            JobSkill(
                name="Python",
                evidence="Preferred Python expertise",
                importance="preferred",
                source_text="Preferred Python expertise"
            )
        ]
    )

    result = default_gap_engine.analyze_gap(resume, jd)
    # Duplicate required JD skills should be deduplicated to 1 requirement
    # Duplicate preferred Python skill should be removed because Python is already required
    assert len(result.matched_skills) == 1
    assert len(result.missing_preferred_skills) == 0
    assert result.summary["total_required_skills"] == 1
    assert result.summary["total_preferred_skills"] == 0
    assert result.overall_match_score == 100.0


def test_deterministic_match_score():
    resume = ResumeProfile(
        skills=[
            ResumeSkill(
                name="Python",
                evidence="Python dev",
                source_section="Skills",
                confidence=1.0
            ),
            ResumeSkill(
                name="React Native",
                evidence="React Native app",
                source_section="Skills",
                confidence=0.9
            )
        ]
    )
    jd = JobDescription(
        required_skills=[
            JobSkill(name="Python", evidence="req 1", importance="required", source_text="req 1"),
            JobSkill(name="React.js", evidence="req 2", importance="required", source_text="req 2"),
            JobSkill(name="Java", evidence="req 3", importance="required", source_text="req 3")
        ],
        preferred_skills=[
            JobSkill(name="Docker", evidence="pref 1", importance="preferred", source_text="pref 1")
        ]
    )

    # Required skills: Python (1.0), React.js (partial 0.5), Java (missing 0.0) -> Avg = (1.0 + 0.5 + 0.0) / 3 = 0.5
    # Preferred skills: Docker (missing 0.0) -> Avg = 0.0
    # Formula: 0.70 * 0.5 + 0.30 * 0.0 = 0.35 -> 35.0%
    result = default_gap_engine.analyze_gap(resume, jd)
    assert result.overall_match_score == 35.0

    # Repeat analysis to confirm determinism
    result2 = default_gap_engine.analyze_gap(resume, jd)
    assert result.overall_match_score == result2.overall_match_score
    assert result.model_dump() == result2.model_dump()


def test_empty_preferred_skills():
    resume = ResumeProfile(
        skills=[
            ResumeSkill(
                name="Python",
                evidence="Python dev",
                source_section="Skills",
                confidence=1.0
            )
        ]
    )
    jd = JobDescription(
        required_skills=[
            JobSkill(name="Python", evidence="req 1", importance="required", source_text="req 1"),
            JobSkill(name="SQL", evidence="req 2", importance="required", source_text="req 2")
        ],
        preferred_skills=[]
    )

    # Required skills: Python (1.0), SQL (0.0) -> Avg = 0.5
    # Preferred skills: empty -> 100% weight on required -> 50.0%
    result = default_gap_engine.analyze_gap(resume, jd)
    assert result.overall_match_score == 50.0


def test_evidence_preservation():
    resume = ResumeProfile(
        skills=[
            ResumeSkill(
                name="Microsoft Excel",
                evidence="Built complex financial models in Excel",
                source_section="Experience",
                confidence=1.0
            )
        ]
    )
    jd = JobDescription(
        required_skills=[
            JobSkill(
                name="MS Excel",
                evidence="Candidate must be proficient in MS Excel",
                importance="required",
                source_text="Candidate must be proficient in MS Excel"
            )
        ]
    )

    result = default_gap_engine.analyze_gap(resume, jd)
    item = result.matched_skills[0]
    assert item.original_jd_wording == "MS Excel"
    assert item.original_resume_wording == "Microsoft Excel"
    assert item.jd_evidence == "Candidate must be proficient in MS Excel"
    assert item.resume_evidence == "Built complex financial models in Excel"
    assert "matched_evidence" in result.evidence
    assert len(result.evidence["matched_evidence"]) == 1


def test_gap_api_endpoint():
    payload = {
        "resume_profile": {
            "name": "Jane Doe",
            "skills": [
                {
                    "name": "Python",
                    "evidence": "4 years Python backend experience",
                    "source_section": "Skills",
                    "confidence": 1.0
                }
            ],
            "experience": [],
            "education": [],
            "projects": [],
            "certifications": []
        },
        "job_description": {
            "role": "Backend Engineer",
            "required_skills": [
                {
                    "name": "Python",
                    "evidence": "Strong Python knowledge required",
                    "importance": "required",
                    "source_text": "Strong Python knowledge required"
                }
            ],
            "preferred_skills": [],
            "responsibilities": [],
            "qualifications": []
        }
    }

    response = client.post("/api/gap/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "overall_match_score" in data
    assert data["overall_match_score"] == 100.0
    assert len(data["matched_skills"]) == 1
    assert data["matched_skills"][0]["normalized_skill_name"] == "python"
