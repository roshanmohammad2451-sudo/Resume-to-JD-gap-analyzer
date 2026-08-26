import pymupdf as fitz
import httpx
import sys

def create_sample_resume_pdf() -> bytes:
    doc = fitz.open()
    
    # Page 1: Profile & Experience
    page1 = doc.new_page()
    page1.insert_text((50, 50), "John Doe - Senior Software Engineer\nEmail: john@example.com | Phone: (555) 123-4567\n", fontsize=14)
    page1.insert_text((50, 100), "SUMMARY:\nPassionate Software Engineer with 6+ years of experience building scalable backend APIs in Python (FastAPI, Django) and high-performance web frontends in React and TypeScript.\n", fontsize=10)
    page1.insert_text((50, 170), "WORK EXPERIENCE:\nSenior Backend Engineer - TechCorp (2021 - Present)\n- Architected microservices serving 2M+ monthly active users using FastAPI and PostgreSQL.\n- Integrated OpenAI structured outputs and pgvector for semantic search.\n", fontsize=10)

    # Page 2: Education & Skills
    page2 = doc.new_page()
    page2.insert_text((50, 50), "SKILLS & EDUCATION:\n", fontsize=14)
    page2.insert_text((50, 90), "Programming Languages: Python, TypeScript, JavaScript, SQL\nFrameworks: FastAPI, React, Vite, Node.js, Tailwind CSS\nDatabases: PostgreSQL, Redis, pgvector\nTools: Docker, Git, CI/CD, PyTest\n\nEDUCATION:\nB.S. in Computer Science - University of Technology (2017 - 2021)", fontsize=10)

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes

def main():
    print("Generating sample PDF resume in-memory...")
    pdf_bytes = create_sample_resume_pdf()
    
    print("Sending POST request to http://127.0.0.1:8000/api/resume/extract...")
    files = {"file": ("john_doe_resume.pdf", pdf_bytes, "application/pdf")}
    
    try:
        response = httpx.post("http://127.0.0.1:8000/api/resume/extract", files=files, timeout=10.0)
        print(f"HTTP Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Successfully extracted PDF!")
            print(f"File Name: {data['file_name']}")
            print(f"Total Pages: {data['total_pages']}")
            for page in data["pages"]:
                print(f"--- Page {page['page_number']} ---")
                print(page["text"][:150] + "...")
        else:
            print(f"Extraction failed: {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"Error connecting to backend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
