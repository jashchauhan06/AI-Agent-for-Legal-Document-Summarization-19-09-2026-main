import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.models import User, Document, LegalAnalysis
from services.auth_service import register_user

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_user_data_isolation(db_session):
    # Register User A and User B
    _, _, user_a = register_user(db_session, "User A", "usera@example.com", "Password123", "Password123")
    _, _, user_b = register_user(db_session, "User B", "userb@example.com", "Password123", "Password123")

    # User A creates a document and analysis
    doc_a = Document(user_id=user_a.id, filename="user_a_contract.pdf", file_type=".pdf", file_size=1024, storage_path="/tmp/a.pdf", document_type="NDA")
    db_session.add(doc_a)
    db_session.commit()

    analysis_a = LegalAnalysis(
        document_id=doc_a.id,
        user_id=user_a.id,
        executive_summary="User A Confidential Summary",
        parties=[], key_terms=[], important_clauses=[], obligations=[], rights=[], deadlines=[],
        financial_terms=[], termination_terms=[], confidentiality_terms=[], intellectual_property=[],
        liability=[], dispute_resolution=[], risk_flags=[], missing_information=[], lawyer_questions=[]
    )
    db_session.add(analysis_a)
    db_session.commit()

    # User B tries to query User A's analysis by ID with User B's user_id scope
    query_as_b = db_session.query(LegalAnalysis).filter(
        LegalAnalysis.id == analysis_a.id,
        LegalAnalysis.user_id == user_b.id
    ).first()

    # Must be None (isolated!)
    assert query_as_b is None

    # User A query returns the analysis
    query_as_a = db_session.query(LegalAnalysis).filter(
        LegalAnalysis.id == analysis_a.id,
        LegalAnalysis.user_id == user_a.id
    ).first()
    assert query_as_a is not None
    assert query_as_a.executive_summary == "User A Confidential Summary"
