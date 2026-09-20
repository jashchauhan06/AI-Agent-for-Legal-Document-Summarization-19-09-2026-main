import os
import pytest
from pathlib import Path
from services.document_extraction_service import (
    extract_txt_text, extract_pdf_text, extract_docx_text, extract_document_text,
    validate_document_file, DocumentExtractionError
)

@pytest.fixture
def tmp_files(tmp_path):
    txt_file = tmp_path / "sample_contract.txt"
    txt_file.write_text(
        "NON-DISCLOSURE AGREEMENT\n\nThis Agreement is entered into by and between Company A and Company B.\n"
        "SECTION 1. CONFIDENTIAL INFORMATION\n"
        "The receiving party shall keep all technical data confidential for a period of 3 years.",
        encoding="utf-8"
    )
    
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("", encoding="utf-8")

    invalid_ext = tmp_path / "script.py"
    invalid_ext.write_text("print('hello')", encoding="utf-8")

    return {
        "txt": str(txt_file),
        "empty": str(empty_file),
        "invalid": str(invalid_ext)
    }


def test_txt_extraction(tmp_files):
    text, meta = extract_txt_text(tmp_files["txt"])
    assert "NON-DISCLOSURE AGREEMENT" in text
    assert "Company A" in text


def test_file_validation(tmp_files):
    is_valid, msg = validate_document_file(tmp_files["txt"])
    assert is_valid is True

    is_valid, msg = validate_document_file(tmp_files["empty"])
    assert is_valid is False
    assert "empty" in msg.lower()

    is_valid, msg = validate_document_file(tmp_files["invalid"])
    assert is_valid is False
    assert "unsupported" in msg.lower()


def test_extraction_dispatcher(tmp_files):
    text, meta = extract_document_text(tmp_files["txt"])
    assert len(text) > 50
    assert "SECTION 1" in text
