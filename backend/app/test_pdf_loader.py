
from pathlib import Path
import sys

# Add the backend folder to Python's import path
BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.rag.pdf_loader import load_pdf

# AURA project root
PROJECT_ROOT = BACKEND_DIR.parent

# Verxeon PDF location
PDF_PATH = PROJECT_ROOT / "data" / "verxeon" / "company_profile.pdf"


if __name__ == "__main__":

    documents = load_pdf(PDF_PATH)

    print("\nPDF extraction successful!")
    print(f"Total extracted pages: {len(documents)}")

    for document in documents:
        print("\n----------------------------")
        print("Source:", document["source"])
        print("Page:", document["page"])
        print("Extracted Text:")
        print(document["text"][:500])
