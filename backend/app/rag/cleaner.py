
import re
import math
from collections import Counter


def normalize_text(text):
    """Normalize extracted PDF text without deleting meaningful content."""

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove invisible control characters
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", text)

    # Normalize spaces while preserving line breaks
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def find_repeated_footer_lines(documents):
    """Find exact lines repeated near the bottom of multiple pages."""

    if len(documents) < 2:
        return set()

    footer_candidates = []

    for document in documents:
        lines = [
            line.strip()
            for line in document["text"].splitlines()
            if line.strip()
        ]

        footer_candidates.extend(lines[-4:])

    counts = Counter(footer_candidates)

    minimum_occurrences = max(
        2,
        math.ceil(len(documents) * 0.6)
    )

    repeated_lines = set()

    for line, count in counts.items():

        if count < minimum_occurrences:
            continue

        if re.search(r"\bconfidential\b", line, re.IGNORECASE):
            continue

        if len(line) > 150:
            continue

        repeated_lines.add(line)

    return repeated_lines


def remove_confidential_watermarks(text):
    """
    Remove standalone Confidential watermark lines and
    an identifiable trailing watermark artifact.

    Preserve ordinary confidentiality statements.
    """

    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()

        # Remove standalone watermark lines only
        if re.fullmatch(
            r"confidential",
            stripped,
            re.IGNORECASE
        ):
            continue

        # Remove trailing watermark only when separated
        # from the preceding sentence by at least two spaces.
        line = re.sub(
            r"\s{2,}Confidential\s*$",
            "",
            line,
            flags=re.IGNORECASE
        )

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)



def repair_hyphenated_words(text):
    """
    Repair words split by PDF extraction while preserving
    legitimate hyphens in compound words.
    """

    # Join words split across lines:
    # per-
    # formance -> performance
    text = re.sub(
        r"(?<=[A-Za-z])-\s*\n\s*(?=[a-z])",
        "",
        text
    )

    # Repair known words split by a hyphen and space
    replacements = {
        "communi- cation": "communication",
        "es- calation": "escalation",
        "per- formance": "performance",
    }

    for incorrect, corrected in replacements.items():
        text = text.replace(incorrect, corrected)

    # Repair a known compound word whose hyphen was
    # separated from the following word by PDF extraction
    text = text.replace(
        "Production- ready",
        "Production-ready"
    )

    return text



def repair_known_concatenations(text):
    """
    Repair only known concatenated terms.
    Avoid general word splitting.
    """

    replacements = {
        "subjectline": "subject line",
        "ClientSuccessManager": "Client Success Manager",
        "integrations,timeline": "integrations, timeline",
        "Productionready": "Production-ready",
    }

    for incorrect, corrected in replacements.items():
        text = text.replace(incorrect, corrected)

    return text


def clean_documents(documents):
    """Clean page-level documents while preserving page metadata."""

    repeated_footers = find_repeated_footer_lines(documents)

    cleaned_documents = []

    for document in documents:

        text = normalize_text(document["text"])

        lines = text.splitlines()
        cleaned_lines = []

        for index, line in enumerate(lines):

            stripped = line.strip()

            if not stripped:
                cleaned_lines.append("")
                continue

            # Remove exact repeated footer lines
            if stripped in repeated_footers:
                continue

            # Remove standalone page numbers at page edges
            is_first_or_last_line = (
                index <= 1 or index >= len(lines) - 2
            )

            if is_first_or_last_line and re.fullmatch(
                r"\d{1,4}", stripped
            ):
                continue

            cleaned_lines.append(line)

        cleaned_text = "\n".join(cleaned_lines)

        # Targeted text cleaning
        cleaned_text = remove_confidential_watermarks(cleaned_text)
        cleaned_text = repair_hyphenated_words(cleaned_text)
        cleaned_text = repair_known_concatenations(cleaned_text)

        # Normalize blank lines again
        cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)
        cleaned_text = cleaned_text.strip()

        if cleaned_text:
            cleaned_documents.append({
                **document,
                "text": cleaned_text
            })

    return cleaned_documents
