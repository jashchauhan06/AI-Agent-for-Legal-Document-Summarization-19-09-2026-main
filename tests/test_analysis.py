import pytest
from services.legal_analysis_service import LegalAnalysisService
from schemas.legal_schemas import LegalAnalysis, DocumentClassification

SAMPLE_NDA_TEXT = """
MUTUAL NON-DISCLOSURE AGREEMENT

This Mutual Non-Disclosure Agreement ("Agreement") is entered into by and between Alpha Technologies Inc. ("Disclosing Party") and Beta Solutions LLC ("Receiving Party").

SECTION 1. PURPOSE AND CONFIDENTIAL INFORMATION
The parties wish to explore a potential business relationship. Receiving Party agrees to hold all proprietary trade secrets, financial records, and software code strictly confidential for a duration of 2 years following termination.

SECTION 2. TERM AND TERMINATION
This Agreement shall commence on January 1, 2026, and continue for a term of 1 year. Either party may terminate this Agreement upon 30 days written notice.

SECTION 3. OBLIGATIONS AND PAYMENT
Receiving Party shall pay a consultation fee of $10,000 within 30 days of invoice receipt.

SECTION 4. INDEMNIFICATION AND LIABILITY
Receiving Party agrees to indemnify and hold harmless Disclosing Party against third-party claims arising from unauthorized disclosure. Total aggregate liability is capped at $50,000.

SECTION 5. GOVERNING LAW
This Agreement shall be governed by the laws of the State of California.
"""


def test_document_classification():
    service = LegalAnalysisService()
    classification = service.classify_document(SAMPLE_NDA_TEXT)
    assert classification.document_type == "NDA"
    assert classification.confidence >= 0.8


def test_legal_analysis_structured_output():
    service = LegalAnalysisService()
    analysis = service.analyze_document(SAMPLE_NDA_TEXT)

    assert isinstance(analysis, LegalAnalysis)
    assert analysis.document_type == "NDA"
    assert len(analysis.parties) >= 2
    assert "Alpha Technologies" in analysis.parties[0].name or "Alpha Technologies" in analysis.parties[1].name or "Beta Solutions" in analysis.parties[0].name
    assert len(analysis.important_clauses) >= 1
    assert len(analysis.obligations) >= 1
    assert len(analysis.financial_terms) >= 1
    assert len(analysis.deadlines) >= 1
    assert len(analysis.potential_risk_flags) >= 1
    assert len(analysis.questions_for_legal_review) >= 1


def test_document_chunking():
    service = LegalAnalysisService()
    long_text = SAMPLE_NDA_TEXT * 20
    chunks = service._chunk_document(long_text, max_chars=2000)
    assert len(chunks) > 1
    assert sum(len(c) for c in chunks) >= len(long_text) - 1000
