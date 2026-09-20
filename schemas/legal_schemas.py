from typing import List, Optional
from pydantic import BaseModel, Field


class DocumentClassification(BaseModel):
    document_type: str = Field(..., description="Likely document type e.g. NDA, Employment Agreement, Lease, etc.")
    confidence: float = Field(..., description="Confidence score between 0.0 and 1.0")


class Party(BaseModel):
    name: str = Field(..., description="Name of the party or entity")
    role: str = Field(..., description="Role in the document (e.g. Service Provider, Employer, Lessee)")
    organization: Optional[str] = Field("Not specified", description="Company or organization name")
    responsibilities: List[str] = Field(default_factory=list, description="Key obligations or duties")


class KeyTerm(BaseModel):
    term: str = Field(..., description="Name of the key term")
    description: str = Field(..., description="Plain-English explanation of the term")
    clause_reference: str = Field("Not specified", description="Section or clause citation")


class ImportantClause(BaseModel):
    clause_number: str = Field(..., description="Section number or clause identifier")
    clause_title: str = Field(..., description="Title or heading of the clause")
    plain_english_explanation: str = Field(..., description="Clear summary preserving legal accuracy")
    source_reference: str = Field(..., description="Source clause number or excerpt reference")


class Obligation(BaseModel):
    party: str = Field(..., description="Party bound by the obligation")
    obligation: str = Field(..., description="Detailed obligation statement")
    deadline_trigger: str = Field("Not specified", description="Timing, deadline, or triggering event")
    source_clause: str = Field("Not specified", description="Clause citation")


class Right(BaseModel):
    party: str = Field(..., description="Party holding the right")
    right: str = Field(..., description="Description of the right granted")
    source_clause: str = Field("Not specified", description="Clause citation")


class Deadline(BaseModel):
    event: str = Field(..., description="Event or milestone requiring compliance")
    date_or_period: str = Field(..., description="Explicit date, timeframe, or notice period")
    source_clause: str = Field("Not specified", description="Section reference")


class FinancialTerm(BaseModel):
    item: str = Field(..., description="Financial category (Fee, Deposit, Interest, Penalty, Tax, etc.)")
    amount_or_terms: str = Field(..., description="Monetary value, formula, or payment schedule")
    source_clause: str = Field("Not specified", description="Clause citation")


class TerminationTerm(BaseModel):
    category: str = Field(..., description="Category (Notice, Cause, Cure Period, Post-Termination, etc.)")
    provision: str = Field(..., description="Plain English description of termination term")
    source_clause: str = Field("Not specified", description="Clause citation")


class ConfidentialityTerm(BaseModel):
    provision: str = Field(..., description="Confidentiality obligation or restriction")
    scope: str = Field("Not specified", description="Scope of protected information")
    duration: str = Field("Not specified", description="Survival duration")
    source_clause: str = Field("Not specified", description="Clause citation")


class IntellectualPropertyTerm(BaseModel):
    provision: str = Field(..., description="IP ownership, assignment, or license provision")
    ownership_or_license: str = Field("Not specified", description="Ownership status or license terms")
    source_clause: str = Field("Not specified", description="Clause citation")


class LiabilityTerm(BaseModel):
    provision: str = Field(..., description="Liability limitation or indemnification term")
    cap_or_exception: str = Field("Not specified", description="Liability cap, exclusions, or exceptions")
    source_clause: str = Field("Not specified", description="Clause citation")


class DisputeResolutionTerm(BaseModel):
    aspect: str = Field(..., description="Aspect (Governing Law, Jurisdiction, Arbitration, Venue)")
    details: str = Field(..., description="Specific legal mechanism or location")
    source_clause: str = Field("Not specified", description="Clause citation")


class PotentialRiskFlag(BaseModel):
    issue: str = Field(..., description="Neutral label of potential area worth reviewing")
    explanation: str = Field(..., description="Objective explanation of the provision")
    source_clause: str = Field(..., description="Source clause number or section reference")
    review_reason: str = Field(..., description="Reason this provision may deserve professional legal review")


class MissingInfo(BaseModel):
    item: str = Field(..., description="Missing or ambiguous legal element")
    details: str = Field(..., description="Explanation of why it appears incomplete or missing")


class LawyerQuestion(BaseModel):
    question: str = Field(..., description="Actionable question to discuss with a lawyer")
    context_or_clause: str = Field("Not specified", description="Relevant clause or background context")


class LegalAnalysis(BaseModel):
    document_type: str = Field("Unclassified", description="Identified legal document type")
    confidence: float = Field(0.9, description="Classification confidence score")
    executive_summary: str = Field(..., description="Concise executive summary answering core questions")
    parties: List[Party] = Field(default_factory=list)
    key_terms: List[KeyTerm] = Field(default_factory=list)
    important_clauses: List[ImportantClause] = Field(default_factory=list)
    obligations: List[Obligation] = Field(default_factory=list)
    rights: List[Right] = Field(default_factory=list)
    deadlines: List[Deadline] = Field(default_factory=list)
    financial_terms: List[FinancialTerm] = Field(default_factory=list)
    termination_terms: List[TerminationTerm] = Field(default_factory=list)
    confidentiality_terms: List[ConfidentialityTerm] = Field(default_factory=list)
    intellectual_property: List[IntellectualPropertyTerm] = Field(default_factory=list)
    liability: List[LiabilityTerm] = Field(default_factory=list)
    dispute_resolution: List[DisputeResolutionTerm] = Field(default_factory=list)
    potential_risk_flags: List[PotentialRiskFlag] = Field(default_factory=list)
    missing_or_unclear_information: List[MissingInfo] = Field(default_factory=list)
    questions_for_legal_review: List[LawyerQuestion] = Field(default_factory=list)
