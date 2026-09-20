import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    analyses = relationship("LegalAnalysis", back_populates="user", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    storage_path = Column(String(512), nullable=False)
    document_type = Column(String(100), default="Unclassified", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="documents")
    analyses = relationship("LegalAnalysis", back_populates="document", cascade="all, delete-orphan")


class LegalAnalysis(Base):
    __tablename__ = "legal_analyses"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    executive_summary = Column(Text, nullable=False)
    parties = Column(JSON, nullable=False, default=list)
    key_terms = Column(JSON, nullable=False, default=list)
    important_clauses = Column(JSON, nullable=False, default=list)
    obligations = Column(JSON, nullable=False, default=list)
    rights = Column(JSON, nullable=False, default=list)
    deadlines = Column(JSON, nullable=False, default=list)
    financial_terms = Column(JSON, nullable=False, default=list)
    termination_terms = Column(JSON, nullable=False, default=list)
    confidentiality_terms = Column(JSON, nullable=False, default=list)
    intellectual_property = Column(JSON, nullable=False, default=list)
    liability = Column(JSON, nullable=False, default=list)
    dispute_resolution = Column(JSON, nullable=False, default=list)
    risk_flags = Column(JSON, nullable=False, default=list)
    missing_information = Column(JSON, nullable=False, default=list)
    lawyer_questions = Column(JSON, nullable=False, default=list)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="analyses")
    document = relationship("Document", back_populates="analyses")
