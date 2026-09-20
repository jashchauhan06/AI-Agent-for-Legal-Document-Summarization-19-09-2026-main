import html
from typing import Dict, Any, Union
from schemas.legal_schemas import LegalAnalysis

LEGAL_DISCLAIMER_TEXT = (
    "IMPORTANT DISCLAIMER:\n"
    "This AI-generated analysis is provided strictly for informational and educational purposes only. "
    "It does NOT constitute legal advice, does not form an attorney-client relationship, and should not be "
    "relied upon as a substitute for professional legal review by a qualified attorney. "
    "AI-generated summaries may contain errors, omissions, or misinterpretations. Always consult a licensed attorney "
    "for legal decisions or advice regarding your specific circumstances."
)


def generate_markdown_report(filename: str, doc_type: str, date_analyzed: str, analysis: Union[LegalAnalysis, Dict[str, Any]]) -> str:
    """Generate comprehensive structured Markdown legal analysis report."""
    if isinstance(analysis, dict):
        # Convert dict to pydantic if needed
        analysis = LegalAnalysis(**analysis)

    lines = []
    lines.append(f"# LEGAL DOCUMENT ANALYSIS REPORT")
    lines.append(f"**Document Filename:** {filename}")
    lines.append(f"**Document Classification:** {analysis.document_type}")
    lines.append(f"**Analysis Date:** {date_analyzed}")
    lines.append("")
    lines.append("---")
    lines.append("### LEGAL DISCLAIMER")
    lines.append(f"> {LEGAL_DISCLAIMER_TEXT}")
    lines.append("---")
    lines.append("")

    # 1. Executive Summary
    lines.append("## 1. Executive Summary")
    lines.append(analysis.executive_summary)
    lines.append("")

    # 2. Parties
    lines.append("## 2. Parties & Roles")
    if analysis.parties:
        for p in analysis.parties:
            lines.append(f"- **Party:** {p.name}")
            lines.append(f"  - **Role:** {p.role}")
            lines.append(f"  - **Organization:** {p.organization}")
            if p.responsibilities:
                lines.append(f"  - **Responsibilities:** {', '.join(p.responsibilities)}")
    else:
        lines.append("Not specified in the document.")
    lines.append("")

    # 3. Key Terms
    lines.append("## 3. Key Terms & Definitions")
    if analysis.key_terms:
        for kt in analysis.key_terms:
            lines.append(f"- **{kt.term}** ({kt.clause_reference}): {kt.description}")
    else:
        lines.append("Not specified in the document.")
    lines.append("")

    # 4. Important Clauses
    lines.append("## 4. Important Clauses")
    if analysis.important_clauses:
        for c in analysis.important_clauses:
            lines.append(f"### {c.clause_number} — {c.clause_title}")
            lines.append(f"**Plain-English Explanation:** {c.plain_english_explanation}")
            lines.append(f"**Source Reference:** `{c.source_reference}`")
            lines.append("")
    else:
        lines.append("Not specified in the document.\n")

    # 5. Obligations
    lines.append("## 5. Obligations")
    if analysis.obligations:
        for ob in analysis.obligations:
            lines.append(f"- **{ob.party}**: {ob.obligation}")
            lines.append(f"  - *Deadline/Trigger:* {ob.deadline_trigger} | *Source:* {ob.source_clause}")
    else:
        lines.append("Not specified in the document.")
    lines.append("")

    # 6. Rights
    lines.append("## 6. Rights")
    if analysis.rights:
        for r in analysis.rights:
            lines.append(f"- **{r.party}**: {r.right} (Source: {r.source_clause})")
    else:
        lines.append("Not specified in the document.")
    lines.append("")

    # 7. Important Dates & Deadlines
    lines.append("## 7. Important Dates & Deadlines")
    if analysis.deadlines:
        lines.append("| Event / Milestone | Date / Notice Period | Source Clause |")
        lines.append("| --- | --- | --- |")
        for d in analysis.deadlines:
            lines.append(f"| {d.event} | {d.date_or_period} | {d.source_clause} |")
    else:
        lines.append("Not specified in the document.")
    lines.append("")

    # 8. Financial Terms
    lines.append("## 8. Financial Terms")
    if analysis.financial_terms:
        for ft in analysis.financial_terms:
            lines.append(f"- **{ft.item}:** {ft.amount_or_terms} (Source: {ft.source_clause})")
    else:
        lines.append("Not specified in the document.")
    lines.append("")

    # 9. Termination Analysis
    lines.append("## 9. Termination Analysis")
    if analysis.termination_terms:
        for tt in analysis.termination_terms:
            lines.append(f"- **[{tt.category}]** {tt.provision} (Source: {tt.source_clause})")
    else:
        lines.append("Not specified in the document.")
    lines.append("")

    # 10. Confidentiality Provisions
    lines.append("## 10. Confidentiality Provisions")
    if analysis.confidentiality_terms:
        for ct in analysis.confidentiality_terms:
            lines.append(f"- {ct.provision} | *Scope:* {ct.scope} | *Duration:* {ct.duration} (Source: {ct.source_clause})")
    else:
        lines.append("Not specified in the document.")
    lines.append("")

    # 11. Intellectual Property
    lines.append("## 11. Intellectual Property")
    if analysis.intellectual_property:
        for ip in analysis.intellectual_property:
            lines.append(f"- {ip.provision} | *Terms:* {ip.ownership_or_license} (Source: {ip.source_clause})")
    else:
        lines.append("Not specified in the document.")
    lines.append("")

    # 12. Liability & Indemnification
    lines.append("## 12. Liability & Indemnification")
    if analysis.liability:
        for l in analysis.liability:
            lines.append(f"- {l.provision} | *Cap/Exceptions:* {l.cap_or_exception} (Source: {l.source_clause})")
    else:
        lines.append("Not specified in the document.")
    lines.append("")

    # 13. Dispute Resolution
    lines.append("## 13. Dispute Resolution")
    if analysis.dispute_resolution:
        for dr in analysis.dispute_resolution:
            lines.append(f"- **{dr.aspect}:** {dr.details} (Source: {dr.source_clause})")
    else:
        lines.append("Not specified in the document.")
    lines.append("")

    # 14. Potential Review Areas
    lines.append("## 14. Potential Review Areas (Flags)")
    if analysis.potential_risk_flags:
        for rf in analysis.potential_risk_flags:
            lines.append(f"### [Potential Review Area] {rf.issue}")
            lines.append(f"**Explanation:** {rf.explanation}")
            lines.append(f"**Source Clause:** `{rf.source_clause}`")
            lines.append(f"**Review Reason:** {rf.review_reason}")
            lines.append("")
    else:
        lines.append("No immediate unusual flags identified.\n")

    # 15. Missing / Unclear Information
    lines.append("## 15. Missing or Unclear Information")
    if analysis.missing_or_unclear_information:
        for mi in analysis.missing_or_unclear_information:
            lines.append(f"- **{mi.item}:** {mi.details}")
    else:
        lines.append("No critical missing provisions detected.")
    lines.append("")

    # 16. Questions for Legal Review
    lines.append("## 16. Questions You May Want to Discuss With a Qualified Lawyer")
    if analysis.questions_for_legal_review:
        for q in analysis.questions_for_legal_review:
            lines.append(f"- **Question:** {q.question}")
            lines.append(f"  - *Context/Clause:* {q.context_or_clause}")
    else:
        lines.append("None generated.")
    lines.append("")

    return "\n".join(lines)


def generate_txt_report(filename: str, doc_type: str, date_analyzed: str, analysis: Union[LegalAnalysis, Dict[str, Any]]) -> str:
    """Generate clean plain text legal report."""
    md = generate_markdown_report(filename, doc_type, date_analyzed, analysis)
    # Strip markdown syntax formatting
    txt = md.replace("# ", "").replace("## ", "").replace("### ", "").replace("**", "").replace("`", "").replace(">", "  ")
    return txt


def generate_html_report(filename: str, doc_type: str, date_analyzed: str, analysis: Union[LegalAnalysis, Dict[str, Any]]) -> str:
    """Generate styled printable HTML legal report."""
    md_content = generate_markdown_report(filename, doc_type, date_analyzed, analysis)
    html_body = html.escape(md_content).replace("\n", "<br>")
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Legal Analysis Report - {html.escape(filename)}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #1e293b; max-width: 900px; margin: 40px auto; padding: 20px; background-color: #f8fafc; }}
        .report-card {{ background: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0; padding: 40px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }}
        h1 {{ color: #0f172a; border-bottom: 2px solid #3b82f6; padding-bottom: 10px; }}
        .disclaimer-box {{ background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0; font-size: 0.9em; color: #991b1b; }}
        pre {{ white-space: pre-wrap; font-family: inherit; }}
    </style>
</head>
<body>
    <div class="report-card">
        <pre>{html_body}</pre>
    </div>
</body>
</html>"""
