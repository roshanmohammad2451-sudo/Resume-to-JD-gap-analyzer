import pymupdf as fitz
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def create_sample_pdf_bytes(pages_text: list[str]) -> bytes:
    """Helper to generate a real PDF in-memory using PyMuPDF."""
    doc = fitz.open()
    for text in pages_text:
        page = doc.new_page()
        page.insert_text((50, 50), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_extract_valid_jd_pdf():
    pdf_bytes = create_sample_pdf_bytes([
        "Job Title: Senior Data Engineer\nRequirements: 5+ years of Python, SQL, Docker.",
        "Preferred Qualifications: Kubernetes, AWS cloud architecture, CI/CD pipelines."
    ])

    files = {"file": ("job_description.pdf", pdf_bytes, "application/pdf")}
    response = client.post("/api/jd/extract", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["file_name"] == "job_description.pdf"
    assert data["total_pages"] == 2
    assert len(data["pages"]) == 2
    assert "Senior Data Engineer" in data["pages"][0]["text"]
    assert "Kubernetes" in data["pages"][1]["text"]


def test_extract_jd_invalid_file_extension():
    files = {"file": ("job_description.docx", b"Mock docx bytes", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    response = client.post("/api/jd/extract", files=files)

    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_extract_jd_invalid_mime_type():
    files = {"file": ("job_description.pdf", b"Some text bytes", "image/jpeg")}
    response = client.post("/api/jd/extract", files=files)

    assert response.status_code == 400
    assert "Invalid MIME type" in response.json()["detail"]


def test_extract_jd_empty_file():
    files = {"file": ("empty_jd.pdf", b"", "application/pdf")}
    response = client.post("/api/jd/extract", files=files)

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_extract_jd_corrupt_file():
    files = {"file": ("corrupt_jd.pdf", b"This is plain text with a .pdf extension", "application/pdf")}
    response = client.post("/api/jd/extract", files=files)

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"] or "valid PDF" in response.json()["detail"]


def test_extracted_jd_text_passed_to_analyze(monkeypatch):
    """
    Verifies that text extracted from a JD PDF can be cleanly fed
    into the POST /api/jd/analyze endpoint.
    """
    pdf_bytes = create_sample_pdf_bytes([
        "Role: Python Backend Developer\nRequirements: Python, FastAPI, PostgreSQL.\nResponsibilities: Build microservices."
    ])

    files = {"file": ("backend_dev_jd.pdf", pdf_bytes, "application/pdf")}
    extract_resp = client.post("/api/jd/extract", files=files)
    assert extract_resp.status_code == 200

    extracted_data = extract_resp.json()
    combined_text = "\n".join(p["text"] for p in extracted_data["pages"])
    assert "Python Backend Developer" in combined_text

    # Analyze request payload
    analyze_payload = {"text": combined_text}
    analyze_resp = client.post("/api/jd/analyze", json=analyze_payload)
    assert analyze_resp.status_code == 200
    jd_profile = analyze_resp.json()
    assert "role" in jd_profile
    assert len(jd_profile["required_skills"]) > 0
