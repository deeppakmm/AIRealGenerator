import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("DATA_DIR", BASE_DIR)).expanduser().resolve()
UPLOAD_FOLDER = DATA_DIR / "user_uploads"
REELS_FOLDER = DATA_DIR / "static" / "reels"
