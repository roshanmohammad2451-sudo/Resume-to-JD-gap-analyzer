import pymupdf as fitz
import os

def generate_resume_pdf():
    doc = fitz.open()
    
    # Page 1: Profile & Experience
    page1 = doc.new_page()
    page1_text = """ALEXANDER PIERCE
Senior Full-Stack Software Engineer
Email: alex.pierce@example.com | Phone: (555) 019-2831 | Location: San Francisco, CA
LinkedIn: linkedin.com/in/alexpierce-dev | GitHub: github.com/alexpierce

PROFESSIONAL SUMMARY
Results-driven Senior Software Engineer with over 6 years of experience designing, building, and scaling modern web applications and backend APIs. Proficient in Python, FastAPI, React, TypeScript, and PostgreSQL. Demonstrated expertise in cloud deployment, microservices architecture, and automated testing pipelines.

TECHNICAL SKILLS
- Languages: Python, TypeScript, JavaScript, SQL, HTML5, CSS3
- Frontend: React, Redux, TailwindCSS, Next.js, Vite
- Backend: FastAPI, Django, Flask, Node.js, RESTful APIs, GraphQL
- Databases: PostgreSQL, Redis, MongoDB, pgvector
- DevOps & Tools: Docker, Kubernetes, AWS, GitHub Actions, PyTest, Jest

WORK EXPERIENCE

Lead Software Engineer | CloudTech Solutions (2022 - Present)
- Architected and built high-performance microservices serving over 2M daily active users using FastAPI and PostgreSQL.
- Reduced API latency by 45% through query optimization, Redis caching, and connection pooling.
- Mentored a team of 5 junior and mid-level developers, establishing best engineering practices and code review workflows.

Senior Backend Developer | DataFlow Systems (2019 - 2022)
- Implemented real-time data processing pipelines processing 10M+ events per day with Python and Kafka.
- Spearheaded migration from legacy monolithic backend to containerized Docker services on AWS ECS.
"""
    rect1 = fitz.Rect(50, 50, 550, 750)
    page1.insert_textbox(rect1, page1_text, fontsize=10, fontname="helv")
    
    # Page 2: Education, Projects & Certifications
    page2 = doc.new_page()
    page2_text = """ALEXANDER PIERCE - Resume Page 2

WORK EXPERIENCE (CONTINUED)

Software Engineer | InnovateTech Inc. (2018 - 2019)
- Developed responsive web interface components using React and TypeScript for an enterprise analytics dashboard.
- Integrated payment processing via Stripe API and user authentication with JWT.

EDUCATION

Bachelor of Science in Computer Science
University of California, Berkeley (2014 - 2018)
- GPA: 3.8 / 4.0
- Coursework: Data Structures & Algorithms, Operating Systems, Database Systems, Computer Networks

KEY PROJECTS

AI Resume & Job Matcher
- Developed an intelligent job analyzer using Python, FastAPI, PyMuPDF, and OpenAI API.
- Implemented vector similarity search with PostgreSQL pgvector for semantic skill matching.

CERTIFICATIONS
- AWS Certified Solutions Architect – Associate (2023)
- Certified Kubernetes Application Developer (CKAD) (2022)
"""
    rect2 = fitz.Rect(50, 50, 550, 750)
    page2.insert_textbox(rect2, page2_text, fontsize=10, fontname="helv")

    output_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "sample_resume.pdf")
    doc.save(output_path)
    doc.close()
    print(f"Successfully generated sample resume PDF at: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    generate_resume_pdf()
