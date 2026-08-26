from pydantic import BaseModel, Field
from typing import List


class PageExtraction(BaseModel):
    page_number: int = Field(..., description="1-based index of the PDF page")
    text: str = Field(..., description="Extracted text content of the page")


class PDFExtractionResponse(BaseModel):
    pages: List[PageExtraction] = Field(..., description="List of page extractions")
    total_pages: int = Field(..., description="Total number of pages in the PDF document")
    file_name: str = Field(..., description="Original name of the uploaded PDF file")
