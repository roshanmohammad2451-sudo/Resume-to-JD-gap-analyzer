import pymupdf as fitz  # PyMuPDF
from app.schemas.pdf import PDFExtractionResponse, PageExtraction


class PDFParsingError(Exception):
    """Custom exception raised during PDF parsing failures."""
    pass


def extract_text_from_pdf(file_bytes: bytes, file_name: str) -> PDFExtractionResponse:
    """
    Extracts text page-by-page from raw PDF bytes using PyMuPDF (fitz).
    
    Processing is strictly in-memory without persisting files to disk.
    """
    if not file_bytes:
        raise PDFParsingError("Uploaded file is empty (0 bytes).")

    # Basic header check for PDF signature (%PDF-)
    if not file_bytes.startswith(b"%PDF"):
        raise PDFParsingError("Unsupported file type. File is not a valid PDF document.")

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        raise PDFParsingError(f"Failed to open PDF file: Corrupted or invalid structure ({str(e)})") from e

    try:
        if doc.is_encrypted:
            # Try opening with empty password if encrypted without password
            if not doc.authenticate(""):
                raise PDFParsingError("PDF is password protected and cannot be extracted.")

        total_pages = doc.page_count
        if total_pages == 0:
            raise PDFParsingError("PDF document contains no pages.")

        pages_extracted: list[PageExtraction] = []
        has_any_text = False

        for page_idx in range(total_pages):
            page = doc.load_page(page_idx)
            text = page.get_text("text") or ""
            text = text.strip()
            if text:
                has_any_text = True
            
            pages_extracted.append(
                PageExtraction(
                    page_number=page_idx + 1,
                    text=text
                )
            )

        if not has_any_text:
            raise PDFParsingError("PDF document contains no extractable text.")

        return PDFExtractionResponse(
            pages=pages_extracted,
            total_pages=total_pages,
            file_name=file_name
        )
    except PDFParsingError:
        raise
    except Exception as e:
        raise PDFParsingError(f"Corrupted or unreadable PDF document: {str(e)}") from e
    finally:
        if 'doc' in locals() and doc:
            doc.close()
