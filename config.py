import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

IS_VERCEL = os.getenv("VERCEL") is not None or os.getenv("VERCEL_ENV") is not None

# Configure temporary paths for read-only serverless environment
if IS_VERCEL:
    os.environ["HOME"] = "/tmp"
    os.environ["GRADIO_TEMP_DIR"] = "/tmp"
    os.environ["MPLCONFIGDIR"] = "/tmp"

BASE_DIR = Path(__file__).resolve().parent

# Application secret and environment
APP_SECRET_KEY = os.getenv("APP_SECRET_KEY", "default-legal-ai-secret-key-production")

DEFAULT_DB_URL = "sqlite:////tmp/legal_ai.db" if IS_VERCEL else "sqlite:///./legal_ai.db"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


# Upload Configuration
_max_file_size_str = os.getenv("MAX_FILE_SIZE_MB", "25").strip()
MAX_FILE_SIZE_MB = int(_max_file_size_str) if _max_file_size_str.isdigit() else 25
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
DEFAULT_UPLOAD_DIR = Path("/tmp/uploads") if IS_VERCEL else BASE_DIR / "uploads"
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(DEFAULT_UPLOAD_DIR)))

try:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

# AI Provider Configuration
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini")
AI_API_BASE = os.getenv("AI_API_BASE", "https://api.openai.com/v1")

# Supported Extensions
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
