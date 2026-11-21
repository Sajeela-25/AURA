from uuid import uuid4

from app.rag.pdf_loader import load_pdf
from app.rag.cleaner import clean_documents
from app.rag.chunker import chunk_documents

from app.rag.embeddings import (
    generate_embeddings,
    generate_query_embedding
)

from app.rag.vector_store import (
    store_chunks,
    search_chunks,
    delete_document
)


def ingest_pdf(pdf_path, company_id, document_id=None):

    if not company_id or not company_id.strip():
        raise ValueError("company_id is required.")

    company_id = company_id.strip()
    document_id = document_id or uuid4().hex

    documents = load_pdf(pdf_path)

    cleaned_documents = clean_documents(documents)

    chunks = chunk_documents(
        cleaned_documents,
        chunk_size=1200,
        overlap=150
    )

    if not chunks:
        raise ValueError("No chunks were created.")

    texts = [
        chunk.get("embedding_text", chunk["text"])
        for chunk in chunks
    ]

    embeddings = generate_embeddings(texts)

    delete_document(company_id, document_id)

    store_chunks(
        chunks=chunks,
        embeddings=embeddings,
        company_id=company_id,
        document_id=document_id,
        source=documents[0]["source"]
    )

    return {
        "company_id": company_id,
        "document_id": document_id,
        "pages_extracted": len(documents),
        "chunks_created": len(chunks),
        "embedding_dimensions": len(embeddings[0])
    }


def retrieve_context(question, company_id, top_k=5):

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    query_embedding = generate_query_embedding(question)

    return search_chunks(
        query_embedding=query_embedding,
        company_id=company_id,
        top_k=top_k
    )