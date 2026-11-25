import re

questions = [
    "What are Verxeon pricing plans and service packages?",
    "What does Verxeon offer in Chatbots and Voice AI?",
    "What is Verxeons employee leave policy?"
]

for question in questions:

    words = re.findall(r"\b[a-zA-Z0-9]+\b", question.lower())

    print("\nQUESTION:", question)
    print("WORDS:", words)
