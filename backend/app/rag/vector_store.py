import chromadb

from app.core.config import (
    CHROMA_DIR,
    CHROMA_COLLECTION
)


client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

collection = client.get_or_create_collection(
    name=CHROMA_COLLECTION,
    metadata={"hnsw:space": "cosine"}
)


def store_chunks(
    chunks,
    embeddings,
    company_id,
    document_id,
    source,
    doc_type
):

    if len(chunks) != len(embeddings):
        raise ValueError(
            "Number of chunks and embeddings must match."
        )

    if not chunks:
        return

    ids = []
    documents = []
    metadatas = []

    for chunk, embedding in zip(chunks, embeddings):

        chunk_id = (
            f"{company_id}_{document_id}_"
            f"{chunk['chunk_index']}"
        )

        ids.append(chunk_id)
        documents.append(chunk["text"])

        metadatas.append({
            "company_id": company_id,
            "document_id": document_id,
            "source": source,
            "doc_type": doc_type,
            "section": chunk.get("section", "General"),
            "page_start": chunk["page_start"],
            "page_end": chunk["page_end"],
            "chunk_index": chunk["chunk_index"]
        })

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )


def search_chunks(query_embedding, company_id, top_k=5, doc_type=None):
    filters = [{"company_id": company_id}]

    if doc_type:
        filters.append({"doc_type": doc_type})

    where = filters[0] if len(filters) == 1 else {"$and": filters}

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where,
        include=["documents", "metadatas", "distances"]
    )

    matches = []

    if not results["ids"] or not results["ids"][0]:
        return matches

    for index, chunk_id in enumerate(results["ids"][0]):

        matches.append({
            "id": chunk_id,
            "text": results["documents"][0][index],
            "metadata": results["metadatas"][0][index],
            "distance": results["distances"][0][index]
        })

    return matches


def delete_document(company_id, document_id):

    collection.delete(
        where={
            "$and": [
                {"company_id": company_id},
                {"document_id": document_id}
            ]
        }
    )