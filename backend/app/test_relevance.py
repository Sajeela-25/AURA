import sys
import re

sys.path.insert(0, "backend")

from app.rag.rag_service import retrieve_context

stop = {
    "what", "which", "where", "when", "who", "why", "how",
    "is", "are", "was", "were", "do", "does", "did",
    "the", "a", "an", "of", "in", "on", "at", "to",
    "for", "from", "with", "and", "or", "about",
    "can", "could", "would", "should", "tell", "me",
    "please", "their", "they", "it", "this", "that"
}

def get_keywords(text):
    words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())
    return {
        word for word in words
        if word not in stop and len(word) > 2
    }

questions = [
    "What are Verxeon pricing plans and service packages?",
    "What does Verxeon offer in Chatbots and Voice AI?",
    "What is Verxeons employee leave policy?"
]

for question in questions:

    print("\n" + "=" * 65)
    print("QUESTION:", question)

    chunks = retrieve_context(question, "verxeon", top_k=12)

    question_keywords = get_keywords(question)

    documents = [
        get_keywords(
            chunk.get("text", "") + " " +
            chunk["metadata"].get("section", "")
        )
        for chunk in chunks
    ]

    frequency = {
        word: sum(word in document for document in documents)
        for word in question_keywords
    }

    print("KEYWORD FREQUENCY:", frequency)

    scores = []

    for index, (chunk, document) in enumerate(zip(chunks, documents)):

        keyword_score = sum(
            1 / frequency[word]
            for word in question_keywords
            if frequency[word] > 0 and word in document
        )

        rank_score = 1 / (index + 1)

        total_score = keyword_score + rank_score

        scores.append((
            total_score,
            index + 1,
            chunk["metadata"].get("section")
        ))

    for score, rank, section in sorted(scores, reverse=True)[:6]:
        print(
            "RANK:", rank,
            "| SCORE:", round(score, 4),
            "| SECTION:", section
        )
