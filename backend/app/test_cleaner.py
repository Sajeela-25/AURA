
from pathlib import Path
import sys

# Add backend directory to Python path
BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.rag.pdf_loader import load_pdf
from app.rag.cleaner import clean_documents


# AURA project directory
PROJECT_ROOT = BACKEND_DIR.parent

# Verxeon PDF location
PDF_PATH = (
    PROJECT_ROOT
    / "data"
    / "verxeon"
    / "company_profile.pdf"
)


if __name__ == "__main__":

    # Step 1: Extract PDF text
    documents = load_pdf(PDF_PATH)

    print("PDF extraction completed!")
    print("Original pages:", len(documents))

    # Step 2: Clean extracted text
    cleaned_documents = clean_documents(documents)

    print("\nData cleaning completed!")
    print("Cleaned pages:", len(cleaned_documents))

    # Show first 3 cleaned pages
    for document in cleaned_documents[:3]:

        print("\n----------------------------")
        print("Source:", document["source"])
        print("Page:", document["page"])
        print("Cleaned text:")
        print(document["text"][:1000])
