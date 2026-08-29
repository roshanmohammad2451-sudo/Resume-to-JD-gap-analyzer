import pytest
from app.services.grounding_validator import DeterministicGroundingValidator
from app.services.retrieval_service import RetrievedEvidence


def test_valid_grounded_recommendation_passes():
    validator = DeterministicGroundingValidator()
    evidence = [
        RetrievedEvidence(
            chunk_id="KB-PY-01_c1",
            source_id="KB-PY-001",
            title="Python Core Development",
            section="Core Concepts",
            text="Python functions, list comprehensions, OOP with classes, and RESTful APIs with FastAPI.",
            similarity=0.92,
        )
    ]

    rec = "Focus on Python by implementing modular functions, classes, and a small FastAPI REST API."
    rationale = "Based on Python Core Development (KB-PY-001), mastering functions and FastAPI directly addresses the gap."

    res = validator.validate_recommendation(
        skill="Python",
        recommendation_text=rec,
        rationale_text=rationale,
        retrieved_evidence=evidence,
        cited_source_ids=["KB-PY-001"],
    )

    assert res.is_grounded is True
    assert res.status == "grounded"
    assert len(res.reasons) == 0


def test_invented_url_rejected():
    validator = DeterministicGroundingValidator()
    evidence = [
        RetrievedEvidence(
            chunk_id="KB-PY-01_c1",
            source_id="KB-PY-001",
            title="Python Core Development",
            section="Core Concepts",
            text="Python functions and dictionary structures.",
            similarity=0.85,
        )
    ]

    rec = "Learn Python by visiting https://fakecourse.com/python-101 and watching videos."
    rationale = "This course covers Python."

    res = validator.validate_recommendation(
        skill="Python",
        recommendation_text=rec,
        rationale_text=rationale,
        retrieved_evidence=evidence,
        cited_source_ids=["KB-PY-001"],
    )

    assert res.is_grounded is False
    assert res.status == "rejected"
    assert any("external URLs" in r for r in res.reasons)


def test_invented_platform_rejected():
    validator = DeterministicGroundingValidator()
    evidence = [
        RetrievedEvidence(
            chunk_id="KB-PY-01_c1",
            source_id="KB-PY-001",
            title="Python Core Development",
            section="Core Concepts",
            text="Python functions and dictionary structures.",
            similarity=0.85,
        )
    ]

    rec = "Take the Coursera Python Masterclass to learn functions."
    rationale = "Coursera has good exercises."

    res = validator.validate_recommendation(
        skill="Python",
        recommendation_text=rec,
        rationale_text=rationale,
        retrieved_evidence=evidence,
        cited_source_ids=["KB-PY-001"],
    )

    assert res.is_grounded is False
    assert res.status == "rejected"
    assert any("external platforms" in r for r in res.reasons)


def test_foreign_unsupported_technology_rejected():
    validator = DeterministicGroundingValidator()
    evidence = [
        RetrievedEvidence(
            chunk_id="KB-PY-01_c1",
            source_id="KB-PY-001",
            title="Python Core Development",
            section="Core Concepts",
            text="Python functions and dictionary structures.",
            similarity=0.85,
        )
    ]

    # Target is Python, but the recommendation introduces Rust and Kubernetes which are not in the chunk
    rec = "Learn Python and then rewrite everything in Rust on Kubernetes."
    rationale = "Rust provides memory safety."

    res = validator.validate_recommendation(
        skill="Python",
        recommendation_text=rec,
        rationale_text=rationale,
        retrieved_evidence=evidence,
        cited_source_ids=["KB-PY-001"],
    )

    assert res.is_grounded is False
    assert res.status == "rejected"
    assert any("unsupported technologies" in r for r in res.reasons)


def test_empty_evidence_fails_safely():
    validator = DeterministicGroundingValidator()
    res = validator.validate_recommendation(
        skill="Python",
        recommendation_text="Learn Python.",
        rationale_text="It is good.",
        retrieved_evidence=[],
        cited_source_ids=[],
    )
    assert res.is_grounded is False
    assert res.status == "insufficient_evidence"
