import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(PROJECT_ROOT / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

EMBEDDING_PROVIDER = os.getenv(
    "EMBEDDING_PROVIDER",
    "local"
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "all-MiniLM-L6-v2"
)

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "gpt-4o-mini"
)

CHROMA_PATH = os.getenv(
    "CHROMA_PATH",
    "data/chroma_db"
)

CHROMA_COLLECTION = os.getenv(
    "CHROMA_COLLECTION",
    "aura_knowledge"
)

UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR = PROJECT_ROOT / CHROMA_PATH