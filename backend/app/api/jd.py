from fastapi import APIRouter, File, UploadFile, HTTPException, status
from app.schemas.pdf import PDFExtractionResponse
from app.schemas.jd import JDAnalyzeRequest, JobDescription
from app.services.pdf_parser import extract_text_from_pdf, PDFParsingError
from app.services.jd_parser import default_jd_parser
from app.services.llm_service import (
    LLMKeyMissingError,
    LLMAPIError,
    LLMParseError,
    LLMServiceError,
)

router = APIRouter()


@router.post(
    "/jd/extract",
    response_model=PDFExtractionResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract page-by-page text from a Job Description PDF",
    description="Accepts a JD PDF upload, extracts text page-by-page in-memory using PyMuPDF, and returns structured page extractions."
)
async def extract_jd_pdf(file: UploadFile = File(...)) -> PDFExtractionResponse:
    file_name = file.filename or "job_description.pdf"

    # Check extension
    if not file_name.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Only PDF files (.pdf) are accepted."
        )

    # Check content type if provided
    if file.content_type and file.content_type not in ["application/pdf", "application/x-pdf", "application/octet-stream"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid MIME type '{file.content_type}'. Only PDF documents are allowed."
        )

    try:
        content = await file.read()
        return extract_text_from_pdf(file_bytes=content, file_name=file_name)
    except PDFParsingError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while processing the JD PDF: {str(e)}"
        )


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
