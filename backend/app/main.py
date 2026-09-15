from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import health, resume, jd, gap, recommendations


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lightweight startup: Avoid expensive pre-indexing or remote calls
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
