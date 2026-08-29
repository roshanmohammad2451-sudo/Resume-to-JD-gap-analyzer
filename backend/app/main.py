from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import health, resume, jd, gap, recommendations
from app.services.knowledge_service import default_knowledge_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Pre-index curated knowledge base
    try:
        await default_knowledge_service.ingest_all()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Knowledge base initial ingestion warning: %s", e)
    yield
    # Shutdown logic if any


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health.router, prefix=settings.API_V1_STR, tags=["health"])
app.include_router(resume.router, prefix=settings.API_V1_STR, tags=["resume"])
app.include_router(jd.router, prefix=settings.API_V1_STR, tags=["jd"])
app.include_router(gap.router, prefix=settings.API_V1_STR, tags=["gap"])
app.include_router(recommendations.router, prefix=settings.API_V1_STR, tags=["recommendations"])


@app.get("/")
def root_endpoint():
    return {
        "name": settings.PROJECT_NAME,
        "status": "running",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health"
    }
