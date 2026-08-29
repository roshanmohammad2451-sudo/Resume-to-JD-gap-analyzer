from fastapi import APIRouter, HTTPException, status
from app.schemas.gap import GapAnalysisRequest, GapAnalysisResponse
from app.services.gap_engine import default_gap_engine

router = APIRouter()


@router.post(
    "/gap/analyze",
    response_model=GapAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Perform deterministic gap analysis between Resume Profile and Job Description",
    description="Compares candidate resume profile against structured job description requirements using explainable, rule-based matching without LLM non-determinism."
)
async def analyze_gap(request: GapAnalysisRequest) -> GapAnalysisResponse:
    try:
        return default_gap_engine.analyze_gap(
            resume_profile=request.resume_profile,
            job_description=request.job_description
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during gap analysis: {str(e)}"
        )
