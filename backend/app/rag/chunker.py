
def chunk_documents(
    documents,
    chunk_size=1200,
    overlap=150
):

    chunks = []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("Invalid overlap value.")

    for document in documents:

        text = document["text"].strip()

        if not text:
            continue

        # First divide text into paragraphs
        paragraphs = [
            p.strip()
            for p in text.split("\n")
            if p.strip()
        ]

        current_chunk = ""
        chunk_number = 1

        for paragraph in paragraphs:

            # Add paragraph if it fits
            if len(current_chunk) + len(paragraph) + 1 <= chunk_size:

                current_chunk += "\n" + paragraph

            else:

                if current_chunk.strip():

                    chunks.append({
                        "text": current_chunk.strip(),
                        "source": document["source"],
                        "page": document["page"],
                        "chunk_id": chunk_number
                    })

                    chunk_number += 1

                # Start next chunk with the new paragraph
                current_chunk = paragraph

        # Save remaining text
        if current_chunk.strip():

            chunks.append({
                "text": current_chunk.strip(),
                "source": document["source"],
                "page": document["page"],
                "chunk_id": chunk_number
            })

    return chunks
