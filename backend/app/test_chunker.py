
from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.rag.pdf_loader import load_pdf
from app.rag.cleaner import clean_documents
from app.rag.chunker import chunk_documents


PROJECT_ROOT = BACKEND_DIR.parent

PDF_PATH = (
    PROJECT_ROOT
    / "data"
    / "verxeon"
    / "company_profile.pdf"
)


if __name__ == "__main__":

    # Step 1: Load PDF
    documents = load_pdf(PDF_PATH)

    print("PDF extraction completed!")
    print("Original pages:", len(documents))

    # Step 2: Clean extracted text
    cleaned_documents = clean_documents(documents)

    print("\nCleaning completed!")
    print("Cleaned pages:", len(cleaned_documents))

    # Step 3: Create chunks from cleaned text
    chunks = chunk_documents(
        cleaned_documents,
        chunk_size=1000,
        overlap=150
    )

    print("\nChunking completed!")
    print("Total chunks:", len(chunks))

    # Step 4: Display first 3 chunks
    for chunk in chunks[:3]:

        print("\n----------------------------")
        print("Source:", chunk["source"])
        print("Page:", chunk["page"])
        print("Chunk ID:", chunk["chunk_id"])
        print("Text:")
        print(chunk["text"])
