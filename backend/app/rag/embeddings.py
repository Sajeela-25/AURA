from app.core.config import (
    EMBEDDING_PROVIDER,
    EMBEDDING_MODEL,
    OPENAI_API_KEY
)

if EMBEDDING_PROVIDER == "local":

    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(EMBEDDING_MODEL)

elif EMBEDDING_PROVIDER == "openai":

    from openai import OpenAI

    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY is required for OpenAI embeddings."
        )

    client = OpenAI(api_key=OPENAI_API_KEY)

else:
    raise ValueError("Unsupported embedding provider.")


def generate_embeddings(texts, batch_size=100):

    if not texts:
        return []

    if EMBEDDING_PROVIDER == "local":

        embeddings = model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embeddings.tolist()

    all_embeddings = []

    for start in range(0, len(texts), batch_size):

        batch = texts[start:start + batch_size]

        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch
        )

        batch_data = sorted(
            response.data,
            key=lambda item: item.index
        )

        all_embeddings.extend(
            item.embedding for item in batch_data
        )

    return all_embeddings


def generate_query_embedding(query):

    if EMBEDDING_PROVIDER == "local":

        embedding = model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embedding.tolist()

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query
    )

    return response.data[0].embedding