import os
import sys
from pathlib import Path

# Force temporary directories for Vercel serverless environment
if os.getenv("VERCEL") or os.getenv("VERCEL_ENV"):
    os.environ["HOME"] = "/tmp"
    os.environ["GRADIO_TEMP_DIR"] = "/tmp"
    os.environ["MPLCONFIGDIR"] = "/tmp"

# Add project root directory to Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import app
