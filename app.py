import sys
import io
from pathlib import Path
from fastapi import FastAPI
import gradio as gr

# Configure stdout for UTF-8 encoding on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add project base directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import IS_VERCEL
from database.connection import init_db
from ui.views import create_legal_ai_ui

# Initialize database
init_db()

# Construct Gradio interface
demo = create_legal_ai_ui()

css_path = Path(__file__).parent / "ui" / "styles.css"
css_content = css_path.read_text(encoding="utf-8") if css_path.exists() else ""

# Enable queueing only when not running in Vercel serverless environment
if not IS_VERCEL:
    demo.queue()

# Top-level ASGI app exported for Vercel deployment
fastapi_app = FastAPI()
app = gr.mount_gradio_app(fastapi_app, demo, path="/", css=css_content)

def main():
    print("Launching local Gradio interface...")
    for attempt_port in range(7860, 7875):
        try:
            print(f"Launching Legal AI Agent on http://127.0.0.1:{attempt_port} ...")
            demo.launch(
                server_name="127.0.0.1",
                server_port=attempt_port,
                share=False,
                show_error=True,
                css=css_content
            )
            break
        except OSError as e:
            if "port" in str(e).lower():
                print(f"Port {attempt_port} is busy, trying next port...")
                continue
            raise e

if __name__ == "__main__":
    main()

