from schemas.legal_schemas import LegalAnalysis


def render_header_html() -> str:
    return """
    <div class="legal-header">
        <h1>⚖️ LegalAI Document Analyzer</h1>
        <p>Production-Grade AI Assistant for Legal Document Processing, Clause Extraction, Risk Identification & Summary</p>
    </div>
    """


def render_disclaimer_html() -> str:
    return """
    <div class="disclaimer-banner">
        <strong>⚠️ IMPORTANT LEGAL NOTICE:</strong> This application provides AI-generated document analysis for informational and educational purposes only. It does <strong>not</strong> constitute legal advice and does not create an attorney-client relationship. AI-generated results may contain errors or omissions. Consult a qualified legal professional for advice about your specific circumstances.
    </div>
    """


def render_progress_html(step_code: int) -> str:
    """Render animated status progress flow checklist."""
    steps = [
        (1, "Document uploaded & validated"),
        (2, "Text extracted & structure cleaned"),
        (3, "Document classification identified"),
        (4, "Analyzing legal structure & clauses"),
        (5, "Extracting obligations & dates"),
        (6, "Identifying risk areas & lawyer questions"),
        (7, "Saving legal analysis to database")
    ]
    
    lines = ['<div class="progress-checklist">']
    for idx, label in steps:
        if idx < step_code:
            lines.append(f'<div class="progress-step done">✓ {label}</div>')
        elif idx == step_code:
            lines.append(f'<div class="progress-step active">● {label}...</div>')
        else:
            lines.append(f'<div class="progress-step pending">○ {label}</div>')
    lines.append('</div>')
    
    if step_code > len(steps):
        return '<div class="progress-checklist"><div class="progress-step done">✓ Legal document analysis complete!</div></div>'
    
    return "\n".join(lines)


def render_metric_card(value: str, label: str) -> str:
    return f"""
    <div class="metric-card">
        <div class="value">{value}</div>
        <div class="label">{label}</div>
    </div>
    """


def format_clauses_markdown(analysis: LegalAnalysis) -> str:
    """Format important clauses with badges and source references."""
    if not analysis.important_clauses:
        return "*No specific clauses highlighted.*"
    
    lines = []
    for c in analysis.important_clauses:
        lines.append(f"### 📌 {c.clause_number}: {c.clause_title}")
        lines.append(f"**Plain-English Explanation:** {c.plain_english_explanation}")
        lines.append(f"`Source Reference: {c.source_reference}`")
        lines.append("---")
    return "\n\n".join(lines)


def format_risks_markdown(analysis: LegalAnalysis) -> str:
    """Format potential risk flags neutrally."""
    if not analysis.potential_risk_flags:
        return "✅ *No immediate unusual review areas identified.*"
    
    lines = []
    for rf in analysis.potential_risk_flags:
        lines.append(f"### ⚠️ Potential Review Area: {rf.issue}")
        lines.append(f"**Explanation:** {rf.explanation}")
        lines.append(f"**Review Reason:** {rf.review_reason}")
        lines.append(f"`Source Clause: {rf.source_clause}`")
        lines.append("---")
    return "\n\n".join(lines)


def format_questions_markdown(analysis: LegalAnalysis) -> str:
    """Format lawyer review questions."""
    if not analysis.questions_for_legal_review:
        return "*No specific questions generated.*"
    
    lines = ["### 💬 Questions You May Want to Discuss With a Qualified Lawyer\n"]
    for idx, q in enumerate(analysis.questions_for_legal_review, 1):
        lines.append(f"**{idx}. {q.question}**")
        lines.append(f"*Context / Clause:* {q.context_or_clause}\n")
    return "\n".join(lines)


def format_missing_info_markdown(analysis: LegalAnalysis) -> str:
    """Format missing or unclear information."""
    if not analysis.missing_or_unclear_information:
        return "✅ *No critical missing provisions detected.*"
    
    lines = ["### ❓ Information Appearing Missing or Unclear\n"]
    for mi in analysis.missing_or_unclear_information:
        lines.append(f"- **{mi.item}:** {mi.details}")
    return "\n".join(lines)
