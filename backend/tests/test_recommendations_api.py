import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_recommendations_api_end_to_end():
    gap_payload = {
        "gap_analysis": {
            "overall_match_score": 60.0,
            "matched_skills": [
                {
                    "normalized_skill_name": "python",
                    "original_jd_wording": "Python",
                    "requirement_importance": "required",
                    "match_status": "matched",
                    "evidence": "Python match",
                }
            ],
            "partial_matches": [
                {
                    "normalized_skill_name": "sql",
                    "original_jd_wording": "PostgreSQL",
                    "requirement_importance": "required",
                    "match_status": "partial",
                    "evidence": "Partial SQL",
                }
            ],
            "missing_required_skills": [
                {
                    "normalized_skill_name": "docker",
                    "original_jd_wording": "Docker",
                    "requirement_importance": "required",
                    "match_status": "missing",
                    "evidence": "Docker missing",
                    "jd_evidence": "Candidate must know Docker containerization",
                }
            ],
            "missing_preferred_skills": [
                {
                    "normalized_skill_name": "unknownfakeskill123",
                    "original_jd_wording": "UnknownFakeSkill123",
                    "requirement_importance": "preferred",
                    "match_status": "missing",
                    "evidence": "Missing fake skill",
                }
            ],
            "experience_gaps": [],
            "qualification_gaps": [],
            "evidence": {},
            "summary": {}
        },
        "max_recommendations": 5
    }

    response = client.post("/api/recommendations/analyze", json=gap_payload)
    assert response.status_code == 200
    data = response.json()

    assert "recommendations" in data
    assert "summary" in data

    recs = data["recommendations"]
    assert len(recs) >= 1

    # Check that Docker (which is in our curated KB) got a grounded recommendation with source_id
    docker_recs = [r for r in recs if r["skill"] == "docker"]
    assert len(docker_recs) == 1
    docker_rec = docker_recs[0]
    assert docker_rec["priority"] == "high"
    assert docker_rec["grounding_status"] == "grounded"
    assert len(docker_rec["source_ids"]) > 0
    assert "KB-DOC-001" in docker_rec["source_ids"]
    assert docker_rec["validation_details"]["is_grounded"] is True

    # Check that unknownfakeskill123 has insufficient_evidence status and no hallucinations
    fake_recs = [r for r in recs if r["skill"] == "unknownfakeskill123"]
    assert len(fake_recs) == 1
    assert fake_recs[0]["grounding_status"] == "insufficient_evidence"
