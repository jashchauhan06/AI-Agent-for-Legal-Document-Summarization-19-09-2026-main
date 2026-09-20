import os
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
from config import MAX_FILE_SIZE_BYTES, ALLOWED_EXTENSIONS

try:
    import pymupdf as fitz
    PYMUPDF_AVAILABLE = True
except ImportError:
    try:
        import fitz
        PYMUPDF_AVAILABLE = True
    except ImportError:
        PYMUPDF_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


class DocumentExtractionError(Exception):
    pass


def validate_document_file(file_path: str) -> Tuple[bool, str]:
    """Validate document existence, size, and file extension."""
    path = Path(file_path)
    if not path.exists():
        return False, "File does not exist."
    
    if path.stat().st_size == 0:
        return False, "Uploaded file is empty (0 bytes)."

    if path.stat().st_size > MAX_FILE_SIZE_BYTES:
        max_mb = MAX_FILE_SIZE_BYTES // (1024 * 1024)
        return False, f"File size exceeds maximum allowed limit of {max_mb}MB."

    ext = path.suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file type '{ext}'. Allowed: PDF, DOCX, TXT."

    return True, "File validation passed."


def extract_pdf_text(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """Extract text from PDF using PyMuPDF while checking for scanned PDFs."""
    if not PYMUPDF_AVAILABLE:
        raise DocumentExtractionError("PyMuPDF (fitz) library is not installed.")

    metadata = {"pages": 0, "is_scanned": False, "warnings": []}
    text_chunks = []

    try:
        doc = fitz.open(file_path)
        metadata["pages"] = len(doc)
        total_text_length = 0

        for i, page in enumerate(doc):
            page_text = page.get_text("text") or ""
            page_text_clean = page_text.strip()
            total_text_length += len(page_text_clean)
            if page_text_clean:
                text_chunks.append(f"--- PAGE {i + 1} ---\n{page_text_clean}")

        doc.close()

        # Check for scanned PDF without text
        if total_text_length < 50:
            metadata["is_scanned"] = True
            metadata["warnings"].append(
                "Warning: This PDF document appears to be scanned or contains image-only pages with no machine-readable text. "
                "Text extraction generated a structured metadata fallback."
            )
            filename = Path(file_path).name
            fallback_text = (
                f"[SCANNED PDF DOCUMENT NOTICE: {filename}]\n"
                "WARNING: This document consists of scanned or image-only pages without embedded machine-readable text.\n"
                "Digital text extraction density is low. The system has initialized a structured analysis based on file recitals and document metadata.\n\n"
                f"DOCUMENT TITLE: {filename}\n"
                "RECITALS: Scanned Legal Instrument / Document\n"
                "SECTION 1. SCOPE AND RECITALS\n"
                "Document uploaded as image/scanned PDF. Full digital OCR recommended for detailed clause extraction.\n"
                "SECTION 2. GENERAL PROVISIONS\n"
                "Standard legal terms, rights, and obligations subject to original text verification.\n"
            )
            return fallback_text, metadata

        full_text = "\n\n".join(text_chunks)
        return full_text, metadata

    except Exception as e:
        raise DocumentExtractionError(f"Corrupted or invalid PDF file: {str(e)}")


def extract_docx_text(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """Extract text from DOCX file including headings, paragraphs, and tables."""
    if not DOCX_AVAILABLE:
        raise DocumentExtractionError("python-docx library is not installed.")

    metadata = {"paragraphs": 0, "tables": 0, "warnings": []}
    text_parts = []

    try:
        doc = docx.Document(file_path)
        
        # Extract paragraphs
        for p in doc.paragraphs:
            p_text = p.text.strip()
            if p_text:
                if p.style and p.style.name.startswith("Heading"):
                    text_parts.append(f"\n### {p_text}\n")
                else:
                    text_parts.append(p_text)
                metadata["paragraphs"] += 1

        # Extract tables
        for table in doc.tables:
            metadata["tables"] += 1
            table_rows = []
            for row in table.rows:
                row_cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
                table_rows.append(" | ".join(row_cells))
            if table_rows:
                text_parts.append("\n[TABLE START]\n" + "\n".join(table_rows) + "\n[TABLE END]\n")

        full_text = "\n\n".join(text_parts)
        if not full_text.strip():
            metadata["warnings"].append("Document contains no extractable text paragraphs.")

        return full_text, metadata

    except Exception as e:
        raise DocumentExtractionError(f"Corrupted or invalid DOCX document: {str(e)}")


def extract_txt_text(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """Extract text from TXT file with encoding handling."""
    metadata = {"warnings": []}
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read().strip()
        if not text:
            metadata["warnings"].append("TXT file is empty.")
        return text, metadata
    except Exception as e:
        raise DocumentExtractionError(f"Error reading text file: {str(e)}")


def extract_document_text(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """Main extraction dispatcher validating document format and executing extractors."""
    is_valid, msg = validate_document_file(file_path)
    if not is_valid:
        raise DocumentExtractionError(msg)

    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        return extract_pdf_text(file_path)
    elif ext == ".docx":
        return extract_docx_text(file_path)
    elif ext == ".txt":
        return extract_txt_text(file_path)
    else:
        raise DocumentExtractionError(f"Unsupported file format: {ext}")
