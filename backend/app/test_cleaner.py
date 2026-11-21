
import sys
from pathlib import Path

# Add the backend directory to Python's import path
BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.rag.pdf_loader import load_pdf
from app.rag.cleaner import clean_documents


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PDF_PATH = PROJECT_ROOT / "data" / "verxeon" / "company_profile.pdf"

documents = load_pdf(PDF_PATH)
cleaned_documents = clean_documents(documents)

print("\n========== CLEANER TEST ==========")

for document in cleaned_documents:
    print(f"\nPAGE: {document['page']}")
    print("=" * 60)
    print(document["text"])

print("\n========== TEST COMPLETED ==========")
