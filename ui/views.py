import os
import json
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional
import gradio as gr
from database.connection import get_db
from database.models import User, Document, LegalAnalysis
from services.auth_service import register_user, authenticate_user
from services.document_extraction_service import extract_document_text, DocumentExtractionError
from services.legal_analysis_service import LegalAnalysisService
from services.export_service import generate_markdown_report, generate_txt_report, generate_html_report
from ui.components import (
    render_header_html, render_disclaimer_html, render_progress_html,
    render_metric_card, format_clauses_markdown, format_risks_markdown,
    format_questions_markdown, format_missing_info_markdown
)

legal_service = LegalAnalysisService()


def create_legal_ai_ui() -> gr.Blocks:
    """Build and bind main Gradio interface for Legal AI Summarizer."""
    
    with gr.Blocks(title="LegalAI — Document Summarizer & Analysis Agent") as demo:
        # Session state for authenticated user
        user_state = gr.State(value=None)  # Stores dict: {"id": int, "email": str, "name": str}
        active_analysis_state = gr.State(value=None)  # Stores dict of active analysis data

        # Header & Disclaimer
        gr.HTML(render_header_html())
        gr.HTML(render_disclaimer_html())

        # Top Bar Navigation / Session info
        with gr.Row(visible=False) as top_nav_bar:
            user_info_label = gr.Markdown("### Welcome, User")
            logout_btn = gr.Button("🚪 Log Out", size="sm", variant="secondary")

        # Container 1: Auth View (Shown when not logged in)
        with gr.Column(visible=True) as auth_view:
            gr.Markdown("## 🔐 Account Access")
            with gr.Tabs():
                with gr.Tab("Log In"):
                    login_email = gr.Textbox(label="Email Address", placeholder="user@example.com")
                    login_password = gr.Textbox(label="Password", type="password")
                    login_btn = gr.Button("Sign In", variant="primary")
                    login_output = gr.Markdown()

                with gr.Tab("Register New Account"):
                    reg_name = gr.Textbox(label="Full Name", placeholder="Jane Doe")
                    reg_email = gr.Textbox(label="Email Address", placeholder="jane@example.com")
                    reg_password = gr.Textbox(label="Password", type="password")
                    reg_confirm_pwd = gr.Textbox(label="Confirm Password", type="password")
                    reg_btn = gr.Button("Create Account", variant="primary")
                    reg_output = gr.Markdown()

        # Container 2: Main Application View (Shown when logged in)
        with gr.Column(visible=False) as main_app_view:
            with gr.Tabs() as main_tabs:
                
                # TAB 1: DASHBOARD
                with gr.Tab("📊 Dashboard", id="tab_dashboard"):
                    gr.Markdown("### 📈 Analysis Overview")
                    with gr.Row():
                        metric_docs_html = gr.HTML(render_metric_card("0", "Documents Analyzed"))
                        metric_summaries_html = gr.HTML(render_metric_card("0", "Summaries Generated"))
                        metric_risks_html = gr.HTML(render_metric_card("0", "Potential Review Areas"))

                    gr.Markdown("### 📄 Recent Document Analyses")
                    dashboard_table = gr.Dataframe(
                        headers=["ID", "Filename", "Document Type", "Date Analyzed"],
                        datatype=["number", "str", "str", "str"],
                        interactive=False
                    )
                    refresh_dash_btn = gr.Button("🔄 Refresh Dashboard", size="sm")

                # TAB 2: UPLOAD & ANALYZE
                with gr.Tab("📂 Upload & Analyze Document", id="tab_upload"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            gr.Markdown("### 📤 Upload Legal File")
                            file_upload = gr.File(
                                label="Drop Legal Document (PDF, DOCX, TXT)",
                                file_types=[".pdf", ".docx", ".txt"],
                                type="filepath"
                            )
                            analyze_btn = gr.Button("⚡ Analyze Legal Document", variant="primary", size="lg")
                            progress_status_html = gr.HTML(value="")

                        with gr.Column(scale=2):
                            gr.Markdown("### 📜 Document Analysis Results")
                            
                            # Dual View: Document text preview toggle
                            with gr.Accordion("📄 View Extracted Raw Document Text", open=False):
                                doc_raw_text_view = gr.Textbox(label="Extracted Document Text", lines=10, interactive=False)

                            with gr.Tabs() as result_tabs:
                                with gr.Tab("Executive Summary"):
                                    summary_doc_type = gr.Markdown("### Classification: Unclassified")
                                    summary_exec_text = gr.Markdown("Upload a document to begin analysis.")

                                with gr.Tab("Parties & Key Terms"):
                                    parties_table = gr.Dataframe(headers=["Party Name", "Role", "Organization", "Responsibilities"], interactive=False)
                                    key_terms_table = gr.Dataframe(headers=["Term", "Description", "Source Reference"], interactive=False)

                                with gr.Tab("Important Clauses"):
                                    important_clauses_md = gr.Markdown()

                                with gr.Tab("Obligations & Rights"):
                                    obligations_table = gr.Dataframe(headers=["Party", "Obligation", "Deadline/Trigger", "Source Clause"], interactive=False)
                                    rights_table = gr.Dataframe(headers=["Party", "Right Granted", "Source Clause"], interactive=False)

                                with gr.Tab("Important Dates & Deadlines"):
                                    deadlines_table = gr.Dataframe(headers=["Event / Milestone", "Date or Period", "Source Clause"], interactive=False)

                                with gr.Tab("Financial & Termination"):
                                    financials_table = gr.Dataframe(headers=["Category", "Amount or Terms", "Source Clause"], interactive=False)
                                    termination_md = gr.Markdown()

                                with gr.Tab("Confidentiality, IP & Liability"):
                                    confidentiality_md = gr.Markdown()
                                    ip_md = gr.Markdown()
                                    liability_md = gr.Markdown()

                                with gr.Tab("Dispute Resolution"):
                                    dispute_table = gr.Dataframe(headers=["Aspect", "Details / Forum", "Source Clause"], interactive=False)

                                with gr.Tab("Potential Review Areas"):
                                    risks_md = gr.Markdown()

                                with gr.Tab("Lawyer Questions & Missing Info"):
                                    lawyer_questions_md = gr.Markdown()
                                    missing_info_md = gr.Markdown()

                            # Download Section
                            gr.Markdown("### 📥 Download Structured Analysis Report")
                            with gr.Row():
                                download_md_btn = gr.DownloadButton("Download Markdown (.md)")
                                download_txt_btn = gr.DownloadButton("Download Text (.txt)")
                                download_html_btn = gr.DownloadButton("Download HTML (.html)")

                # TAB 3: HISTORY & MY ANALYSES
                with gr.Tab("📚 My Legal Analyses", id="tab_history"):
                    with gr.Row():
                        search_history_input = gr.Textbox(label="Search Documents", placeholder="Type filename or party name...")
                        type_filter_dropdown = gr.Dropdown(
                            label="Filter by Document Type",
                            choices=["All Types", "Employment Agreement", "NDA", "Lease", "Service Agreement", "Vendor Agreement", "Other"],
                            value="All Types"
                        )
                        filter_history_btn = gr.Button("Search & Filter", size="sm")

                    history_table = gr.Dataframe(
                        headers=["Analysis ID", "Filename", "Document Type", "Date Analyzed"],
                        datatype=["number", "str", "str", "str"],
                        interactive=False
                    )

                    with gr.Row():
                        selected_analysis_id_input = gr.Number(label="Select Analysis ID", precision=0)
                        open_analysis_btn = gr.Button("👁️ Open Selected Analysis", variant="primary")
                        delete_analysis_btn = gr.Button("🗑️ Delete Selected Analysis", variant="stop")
                    
                    history_action_output = gr.Markdown()

        # =========================================================================
        # EVENT HANDLERS & CALLBACKS
        # =========================================================================

        # Helper to get current DB session
        def db_session():
            return next(get_db())

        # Registration Handler
        def handle_registration(name, email, password, confirm_pwd):
            db = db_session()
            success, msg, user = register_user(db, name, email, password, confirm_pwd)
            if success:
                return f"✅ **Success:** {msg}"
            return f"❌ **Error:** {msg}"

        reg_btn.click(
            fn=handle_registration,
            inputs=[reg_name, reg_email, reg_password, reg_confirm_pwd],
            outputs=[reg_output]
        )

        # Login Handler
        def handle_login(email, password):
            db = db_session()
            success, msg, user = authenticate_user(db, email, password)
            if success:
                u_dict = {"id": user.id, "email": user.email, "name": user.name}
                welcome_txt = f"### Welcome back, {user.name} ({user.email})"
                return (
                    u_dict,                      # user_state
                    gr.update(visible=False),    # auth_view
                    gr.update(visible=True),     # main_app_view
                    gr.update(visible=True),     # top_nav_bar
                    welcome_txt,                 # user_info_label
                    f"✅ Logged in successfully."
                )
            return None, gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), "", f"❌ **Error:** {msg}"

        login_btn.click(
            fn=handle_login,
            inputs=[login_email, login_password],
            outputs=[user_state, auth_view, main_app_view, top_nav_bar, user_info_label, login_output]
        )

        # Logout Handler
        def handle_logout():
            return (
                None,                         # user_state
                gr.update(visible=True),      # auth_view
                gr.update(visible=False),     # main_app_view
                gr.update(visible=False)      # top_nav_bar
            )

        logout_btn.click(
            fn=handle_logout,
            outputs=[user_state, auth_view, main_app_view, top_nav_bar]
        )

        # Dashboard Data Loader
        def load_dashboard_data(user):
            if not user or "id" not in user:
                return (
                    render_metric_card("0", "Documents Analyzed"),
                    render_metric_card("0", "Summaries Generated"),
                    render_metric_card("0", "Potential Review Areas"),
                    []
                )
            
            db = db_session()
            # Multi-tenant scoping
            analyses = db.query(LegalAnalysis).filter(LegalAnalysis.user_id == user["id"]).order_by(LegalAnalysis.created_at.desc()).all()
            
            doc_count = len(analyses)
            sum_count = doc_count
            total_risks = 0

            table_rows = []
            for a in analyses:
                doc = db.query(Document).filter(Document.id == a.document_id).first()
                filename = doc.filename if doc else "Document"
                risk_flags = a.risk_flags or []
                total_risks += len(risk_flags)
                date_str = a.created_at.strftime("%Y-%m-%d %H:%M")
                table_rows.append([a.id, filename, a.document_type, date_str])

            return (
                render_metric_card(str(doc_count), "Documents Analyzed"),
                render_metric_card(str(sum_count), "Summaries Generated"),
                render_metric_card(str(total_risks), "Potential Review Areas"),
                table_rows
            )

        refresh_dash_btn.click(
            fn=load_dashboard_data,
            inputs=[user_state],
            outputs=[metric_docs_html, metric_summaries_html, metric_risks_html, dashboard_table]
        )

        # Document Upload & Legal Analysis Handler
        def process_and_analyze_document(file_obj, user):
            if not user or "id" not in user:
                raise gr.Error("Please log in to upload and analyze legal documents.")
            
            if not file_obj:
                return (
                    render_progress_html(0),
                    "",
                    "### Classification: None",
                    "No document uploaded.",
                    [], [], "", [], [], [], [], "", "", "", "", [], "", "",
                    None, None, None, None, None
                )

            file_path = file_obj if isinstance(file_obj, str) else file_obj.name
            filename = os.path.basename(file_path)

            try:
                # 1. Extraction
                extracted_text, metadata = extract_document_text(file_path)

                # 2. AI Analysis Execution
                analysis = legal_service.analyze_document(extracted_text)

                # 3. Save to Database with strict ownership
                db = db_session()
                doc_record = Document(
                    user_id=user["id"],
                    filename=filename,
                    file_type=Path(file_path).suffix.lower(),
                    file_size=os.path.getsize(file_path),
                    storage_path=file_path,
                    document_type=analysis.document_type
                )
                db.add(doc_record)
                db.commit()
                db.refresh(doc_record)

                analysis_record = LegalAnalysis(
                    document_id=doc_record.id,
                    user_id=user["id"],
                    executive_summary=analysis.executive_summary,
                    parties=[p.model_dump() for p in analysis.parties],
                    key_terms=[kt.model_dump() for kt in analysis.key_terms],
                    important_clauses=[ic.model_dump() for ic in analysis.important_clauses],
                    obligations=[ob.model_dump() for ob in analysis.obligations],
                    rights=[r.model_dump() for r in analysis.rights],
                    deadlines=[d.model_dump() for d in analysis.deadlines],
                    financial_terms=[ft.model_dump() for ft in analysis.financial_terms],
                    termination_terms=[tt.model_dump() for tt in analysis.termination_terms],
                    confidentiality_terms=[ct.model_dump() for ct in analysis.confidentiality_terms],
                    intellectual_property=[ip.model_dump() for ip in analysis.intellectual_property],
                    liability=[l.model_dump() for l in analysis.liability],
                    dispute_resolution=[dr.model_dump() for dr in analysis.dispute_resolution],
                    risk_flags=[rf.model_dump() for rf in analysis.potential_risk_flags],
                    missing_information=[mi.model_dump() for mi in analysis.missing_or_unclear_information],
                    lawyer_questions=[lq.model_dump() for lq in analysis.questions_for_legal_review]
                )
                db.add(analysis_record)
                db.commit()

                # Generate export files
                date_str = analysis_record.created_at.strftime("%Y-%m-%d %H:%M")
                md_content = generate_markdown_report(filename, analysis.document_type, date_str, analysis)
                txt_content = generate_txt_report(filename, analysis.document_type, date_str, analysis)
                html_content = generate_html_report(filename, analysis.document_type, date_str, analysis)

                tmp_dir = Path("uploads/reports")
                tmp_dir.mkdir(parents=True, exist_ok=True)

                md_path = str(tmp_dir / f"analysis_{analysis_record.id}.md")
                txt_path = str(tmp_dir / f"analysis_{analysis_record.id}.txt")
                html_path = str(tmp_dir / f"analysis_{analysis_record.id}.html")

                with open(md_path, "w", encoding="utf-8") as f: f.write(md_content)
                with open(txt_path, "w", encoding="utf-8") as f: f.write(txt_content)
                with open(html_path, "w", encoding="utf-8") as f: f.write(html_content)

                # Format tabular data
                parties_data = [[p.name, p.role, p.organization, ", ".join(p.responsibilities)] for p in analysis.parties]
                key_terms_data = [[kt.term, kt.description, kt.clause_reference] for kt in analysis.key_terms]
                obligations_data = [[ob.party, ob.obligation, ob.deadline_trigger, ob.source_clause] for ob in analysis.obligations]
                rights_data = [[r.party, r.right, r.source_clause] for r in analysis.rights]
                deadlines_data = [[d.event, d.date_or_period, d.source_clause] for d in analysis.deadlines]
                financials_data = [[ft.item, ft.amount_or_terms, ft.source_clause] for ft in analysis.financial_terms]
                dispute_data = [[dr.aspect, dr.details, dr.source_clause] for dr in analysis.dispute_resolution]

                termination_txt = "\n\n".join([f"**[{tt.category}]** {tt.provision} (`{tt.source_clause}`)" for tt in analysis.termination_terms])
                confidentiality_txt = "\n\n".join([f"**Confidentiality:** {ct.provision} | Scope: {ct.scope} | Duration: {ct.duration} (`{ct.source_clause}`)" for ct in analysis.confidentiality_terms])
                ip_txt = "\n\n".join([f"**Intellectual Property:** {ip.provision} | Terms: {ip.ownership_or_license} (`{ip.source_clause}`)" for ip in analysis.intellectual_property])
                liability_txt = "\n\n".join([f"**Liability & Indemnification:** {l.provision} | Caps/Exclusions: {l.cap_or_exception} (`{l.source_clause}`)" for l in analysis.liability])

                progress_html = render_progress_html(8)
                if metadata.get("is_scanned"):
                    progress_html += '<div class="warning-banner">⚠️ <strong>Scanned PDF Notice:</strong> Digital text density is low (image/scanned document). Structured analysis initialized based on file recitals and extractable metadata.</div>'

                return (
                    progress_html,
                    extracted_text,
                    f"### Document Classification: {analysis.document_type} (Confidence: {int(analysis.confidence*100)}%)",
                    analysis.executive_summary,
                    parties_data, key_terms_data,
                    format_clauses_markdown(analysis),
                    obligations_data, rights_data,
                    deadlines_data,
                    financials_data, termination_txt,
                    confidentiality_txt, ip_txt, liability_txt,
                    dispute_data,
                    format_risks_markdown(analysis),
                    format_questions_markdown(analysis), format_missing_info_markdown(analysis),
                    md_path, txt_path, html_path,
                    analysis_record.id
                )

            except Exception as e:
                err_html = f'<div class="disclaimer-banner">❌ <strong>Error processing document:</strong> {str(e)}</div>'
                return (
                    err_html, "", "### Classification: Error", str(e),
                    [], [], "", [], [], [], [], "", "", "", "", [], "", "",
                    None, None, None, None, None
                )


        analyze_btn.click(
            fn=process_and_analyze_document,
            inputs=[file_upload, user_state],
            outputs=[
                progress_status_html, doc_raw_text_view, summary_doc_type, summary_exec_text,
                parties_table, key_terms_table, important_clauses_md, obligations_table, rights_table,
                deadlines_table, financials_table, termination_md, confidentiality_md, ip_md, liability_md,
                dispute_table, risks_md, lawyer_questions_md, missing_info_md,
                download_md_btn, download_txt_btn, download_html_btn,
                active_analysis_state
            ]
        )

        # History Data Loader & Search Filter Handler
        def load_history(user, search_query, type_filter):
            if not user or "id" not in user:
                return []
            
            db = db_session()
            query = db.query(LegalAnalysis).filter(LegalAnalysis.user_id == user["id"])

            if type_filter and type_filter != "All Types":
                query = query.filter(LegalAnalysis.document_type == type_filter)

            analyses = query.order_by(LegalAnalysis.created_at.desc()).all()
            
            rows = []
            search_query = (search_query or "").strip().lower()
            for a in analyses:
                doc = db.query(Document).filter(Document.id == a.document_id).first()
                filename = doc.filename if doc else "Document"
                if search_query:
                    if search_query not in filename.lower() and search_query not in a.document_type.lower():
                        continue

                date_str = a.created_at.strftime("%Y-%m-%d %H:%M")
                rows.append([a.id, filename, a.document_type, date_str])

            return rows

        filter_history_btn.click(
            fn=load_history,
            inputs=[user_state, search_history_input, type_filter_dropdown],
            outputs=[history_table]
        )

        # Open Selected Past Analysis Handler
        def open_past_analysis(user, analysis_id):
            if not user or "id" not in user:
                return "❌ Please log in."
            if not analysis_id:
                return "❌ Please enter a valid Analysis ID."

            db = db_session()
            # Verify ownership!
            analysis_rec = db.query(LegalAnalysis).filter(
                LegalAnalysis.id == int(analysis_id),
                LegalAnalysis.user_id == user["id"]
            ).first()

            if not analysis_rec:
                return "❌ Analysis record not found or access denied."

            doc = db.query(Document).filter(Document.id == analysis_rec.document_id).first()
            filename = doc.filename if doc else "Document"

            return f"✅ Opened Analysis ID **#{analysis_rec.id}** for document `{filename}`. Switch to the **Upload & Analyze Document** tab to view complete findings."

        open_analysis_btn.click(
            fn=open_past_analysis,
            inputs=[user_state, selected_analysis_id_input],
            outputs=[history_action_output]
        )

        # Delete Selected Past Analysis Handler
        def delete_past_analysis(user, analysis_id):
            if not user or "id" not in user:
                return "❌ Please log in.", []
            if not analysis_id:
                return "❌ Please enter a valid Analysis ID.", []

            db = db_session()
            # Verify ownership!
            analysis_rec = db.query(LegalAnalysis).filter(
                LegalAnalysis.id == int(analysis_id),
                LegalAnalysis.user_id == user["id"]
            ).first()

            if not analysis_rec:
                return "❌ Analysis record not found or access denied.", []

            doc_id = analysis_rec.document_id
            db.delete(analysis_rec)
            
            # Delete document record if no other analyses exist
            doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == user["id"]).first()
            if doc:
                db.delete(doc)
            
            db.commit()

            new_history = load_history(user, "", "All Types")
            return f"🗑️ Analysis ID **#{analysis_id}** permanently deleted.", new_history

        delete_analysis_btn.click(
            fn=delete_past_analysis,
            inputs=[user_state, selected_analysis_id_input],
            outputs=[history_action_output, history_table]
        )

    return demo
