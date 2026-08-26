from fastapi import APIRouter, HTTPException, status
from app.schemas.jd import JDAnalyzeRequest, JobDescription
from app.services.jd_parser import default_jd_parser
from app.services.llm_service import (
    LLMKeyMissingError,
    LLMAPIError,
    LLMParseError,
    LLMServiceError,
)

router = APIRouter()


@router.post(
    "/jd/analyze",
    response_model=JobDescription,
    status_code=status.HTTP_200_OK,
    summary="Convert Job Description text into structured JobDescription requirements",
    description="Parses job description text using AI with strict grounding rules to extract role, required skills, preferred skills, responsibilities, and qualifications."
)
async def analyze_job_description(request: JDAnalyzeRequest) -> JobDescription:
    try:
        return await default_jd_parser.analyze_jd_text(request.text)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except LLMKeyMissingError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OpenAI API key is missing or not configured."
        )
    except LLMAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"OpenAI service communication error: {str(e)}"
        )
    except (LLMParseError, LLMServiceError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process job description analysis: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during job description analysis: {str(e)}"
        )
