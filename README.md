# Resume-to-JD Gap Analyzer

An AI-powered application designed to perform deterministic, grounded, and accurate skill-gap analysis between Candidate Resumes and Job Descriptions (JDs).

## Architecture

- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **Backend**: Python 3.10+, FastAPI, Pydantic v2
- **AI / Pipeline**: Structured extraction, skill normalization, deterministic gap engine, RAG retrieval & grounded recommendation generation with deterministic grounding validation
- **Database**: PostgreSQL with `pgvector`

## Directory Structure

```text
resume-jd-gap-analyzer/
├── frontend/          # React + TypeScript + Vite + Tailwind CSS
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── api/       # API Routes & Endpoints
│   │   ├── services/  # Core Domain & Pipeline Business Logic
│   │   ├── schemas/   # Pydantic Schemas
│   │   ├── models/    # Database Models
│   │   ├── db/        # Database Connections & Migrations
│   │   ├── core/      # App Configuration & Settings
│   │   └── main.py    # FastAPI Entrypoint
│   ├── .env.example
│   └── requirements.txt
├── data/              # Taxonomies and local data resources
├── scripts/           # Utility & data processing scripts
├── tests/             # Project test suites
├── .gitignore
└── README.md
```

## Quick Start

### Backend
```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
