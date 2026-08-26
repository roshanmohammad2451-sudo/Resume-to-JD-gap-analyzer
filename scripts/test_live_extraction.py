import httpx
import os
import json

def test_live_pdf_extraction():
    pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "sample_resume.pdf"))
    url = "http://localhost:8000/api/resume/extract"
    
    print(f"Uploading file '{pdf_path}' to '{url}'...")
    
    with open(pdf_path, "rb") as f:
        files = {"file": ("sample_resume.pdf", f, "application/pdf")}
        response = httpx.post(url, files=files, timeout=10.0)
    
    print(f"HTTP Response Status Code: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    data = response.json()
    print("Received Extraction Response:")
    print(json.dumps(data, indent=2))
    
    assert data["file_name"] == "sample_resume.pdf"
    assert data["total_pages"] == 2
    assert len(data["pages"]) == 2
    assert data["pages"][0]["page_number"] == 1
    assert "ALEXANDER PIERCE" in data["pages"][0]["text"]
    assert "Senior Full-Stack Software Engineer" in data["pages"][0]["text"]
    assert data["pages"][1]["page_number"] == 2
    assert "University of California, Berkeley" in data["pages"][1]["text"]
    
    print("\nTesting Error Cases:")
    
    # 1. Non-PDF extension
    files_txt = {"file": ("resume.txt", b"plain text", "text/plain")}
    resp_txt = httpx.post(url, files=files_txt)
    assert resp_txt.status_code == 400
    assert "Unsupported file format" in resp_txt.json()["detail"]
    print("[OK] Non-PDF file rejected with 400 Bad Request.")

    # 2. Empty PDF (0 bytes)
    files_empty = {"file": ("empty.pdf", b"", "application/pdf")}
    resp_empty = httpx.post(url, files=files_empty)
    assert resp_empty.status_code == 400
    assert "empty" in resp_empty.json()["detail"].lower()
    print("[OK] Empty PDF (0 bytes) rejected with 400 Bad Request.")

    # 3. Corrupted PDF
    files_corrupt = {"file": ("corrupted.pdf", b"%PDF-1.4 invalid garbage binary data stream", "application/pdf")}
    resp_corrupt = httpx.post(url, files=files_corrupt)
    assert resp_corrupt.status_code == 400
    print("[OK] Corrupted PDF rejected with 400 Bad Request.")

    print("\nSUCCESS: All live PDF extraction & error handling tests passed!")

if __name__ == "__main__":
    test_live_pdf_extraction()
