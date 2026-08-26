import pymupdf as fitz
import io
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


def create_empty_pdf_bytes() -> bytes:
    """Helper to generate a PDF with 0 pages."""
    doc = fitz.open()
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_extract_valid_pdf():
    pdf_bytes = create_sample_pdf_bytes([
        "Page 1: Senior Software Engineer with Python and FastAPI experience.",
        "Page 2: Education: BS Computer Science, Skills: React, TypeScript, PostgreSQL."
    ])

    files = {"file": ("resume.pdf", pdf_bytes, "application/pdf")}
    response = client.post("/api/resume/extract", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["file_name"] == "resume.pdf"
    assert data["total_pages"] == 2
    assert len(data["pages"]) == 2
    assert data["pages"][0]["page_number"] == 1
    assert "Senior Software Engineer" in data["pages"][0]["text"]
    assert data["pages"][1]["page_number"] == 2
    assert "BS Computer Science" in data["pages"][1]["text"]


def test_extract_invalid_file_extension():
    files = {"file": ("resume.txt", b"Hello world text file", "text/plain")}
    response = client.post("/api/resume/extract", files=files)

    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_extract_invalid_mime_type():
    files = {"file": ("resume.pdf", b"Hello world text file", "image/png")}
    response = client.post("/api/resume/extract", files=files)

    assert response.status_code == 400
    assert "Invalid MIME type" in response.json()["detail"]


def test_extract_empty_pdf():
    # Test 0-byte file
    files = {"file": ("empty.pdf", b"", "application/pdf")}
    response = client.post("/api/resume/extract", files=files)

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_extract_corrupted_pdf():
    # PDF signature with garbage content
    corrupted_bytes = b"%PDF-1.4 garbage corrupted binary data content that is invalid PDF stream"
    files = {"file": ("corrupted.pdf", corrupted_bytes, "application/pdf")}
    response = client.post("/api/resume/extract", files=files)

    assert response.status_code == 400
    assert "corrupted" in response.json()["detail"].lower() or "failed" in response.json()["detail"].lower()
