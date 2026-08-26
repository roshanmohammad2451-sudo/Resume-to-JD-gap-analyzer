from fastapi import APIRouter, File, UploadFile, HTTPException, status
from app.schemas.pdf import PDFExtractionResponse
from app.schemas.resume import ResumeAnalyzeRequest, ResumeProfile
from app.services.pdf_parser import extract_text_from_pdf, PDFParsingError
from app.services.resume_analyzer import default_resume_analyzer
from app.services.llm_service import (
    LLMKeyMissingError,
    LLMAPIError,
    LLMParseError,
    LLMServiceError,
)

router = APIRouter()


@router.post(
    "/resume/extract",
    response_model=PDFExtractionResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract page-by-page text from a candidate PDF resume",
    description="Accepts a PDF upload, extracts text page-by-page completely in-memory using PyMuPDF, and returns structured page extractions."
)
async def extract_resume_pdf(file: UploadFile = File(...)) -> PDFExtractionResponse:
    file_name = file.filename or "resume.pdf"
    
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
            detail=f"An unexpected error occurred while processing the PDF: {str(e)}"
        )


@router.post(
    "/resume/analyze",
    response_model=ResumeProfile,
    status_code=status.HTTP_200_OK,
    summary="Convert extracted resume text into structured ResumeProfile",
    description="Analyzes candidate resume text using structured AI model with strict grounding rules."
)
async def analyze_resume(request: ResumeAnalyzeRequest) -> ResumeProfile:
    try:
        return await default_resume_analyzer.analyze_resume_text(request.text)
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
            detail=f"Failed to process resume analysis: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during resume analysis: {str(e)}"
        )
