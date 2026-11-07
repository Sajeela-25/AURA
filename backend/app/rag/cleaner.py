
import re


# Sections that are only document navigation,
# not actual company knowledge.
TOC_START = "This document answers the 12 data categories requested"
TOC_END = "12\nContact / Escalation\nWho to contact for each issue"


def normalize_text(text):
    """
    Normalize extracted PDF text while preserving
    meaningful headings, bullets and paragraphs.
    """

    if not text:
        return ""

    # Remove invisible control characters
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Normalize spaces and tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Remove spaces at the beginning/end of lines
    lines = [line.strip() for line in text.split("\n")]

    # Remove empty lines
    lines = [line for line in lines if line]

    # Remove consecutive duplicate lines
    cleaned_lines = []

    for line in lines:
        if not cleaned_lines or line != cleaned_lines[-1]:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def remove_table_of_contents(text):
    """
    Remove the introductory category summary from
    the Verxeon document, while retaining the actual
    company information sections.
    """

    start = text.find(TOC_START)

    if start == -1:
        return text

    end = text.find("1. Company Information", start)

    if end == -1:
        return text

    # Retain the document introduction before the TOC
    # and the actual company information after the TOC.
    return text[:start] + text[end:]


def clean_text(text):

    text = normalize_text(text)

    text = remove_table_of_contents(text)

    return text.strip()


def clean_documents(documents):

    cleaned_documents = []

    for document in documents:

        cleaned_content = clean_text(document["text"])

        if not cleaned_content:
            continue

        cleaned_documents.append({
            **document,
            "text": cleaned_content
        })

    return cleaned_documents
