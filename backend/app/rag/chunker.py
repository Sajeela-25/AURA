
import re


def is_heading(line):
    """Identify likely headings using general text-formatting clues."""

    line = line.strip()

    if not line or len(line) > 100:
        return False

    # Markdown headings: ## Company Information
    if re.match(r"^#{1,6}\s+\S", line):
        return True

    # Numbered headings: 1. Company Information
    numbered_heading = re.match(
        r"^\d{1,2}[.)]\s+(.+)$",
        line
    )

    if numbered_heading:
        title = numbered_heading.group(1).strip()

        if len(title) > 60:
            return False

        if title.endswith((".", "?", "!", ",", ";", ":")):
            return False

        if re.search(r"[,?!]", title):
            return False

        words = title.split()

        if len(words) >= 3:
            capitalized_words = sum(
                1 for word in words
                if word[0].isupper()
            )

            if capitalized_words / len(words) < 0.6:
                return False

        return True

    # All-uppercase headings: COMPANY INFORMATION
    letters = re.sub(r"[^A-Za-z]", "", line)

    if (
        len(letters) >= 3
        and line.upper() == line
        and not line.endswith((".", "?", "!"))
    ):
        return True

    # Remove Markdown emphasis markers for further checks
    title = re.sub(r"[*_`]", "", line).strip()

    # Reject sentence-like lines and labels containing colons
    if title.endswith((".", "?", "!", ",", ";", ":")):
        return False

    if ":" in title or "," in title:
        return False

    words = title.split()

    # Ordinary headings usually contain a small number of words
    if not 1 <= len(words) <= 8:
        return False

    # Reject lines that look like complete sentences
    sentence_words = {
        "is", "was", "were", "has", "have", "had",
        "does", "do", "did", "can", "could", "will", "would",
        "should", "must", "may", "might", "provides",
        "offers", "includes", "supports", "collects",
        "requires", "allows", "helps", "focuses"
    }

    if any(word.lower() in sentence_words for word in words):
        return False

    # A likely heading should begin with a capital letter
    if not words[0][0].isupper():
        return False

    return True


def is_list_item(line):
    """Identify common bullet and numbered-list formatting."""

    return bool(
        re.match(
            r"^(?:[-•*▪◦]|\d+[.)])\s+",
            line.strip()
        )
    )


def extract_paragraphs(documents):
    """
    Convert page text into paragraphs.

    Consecutive PDF-wrapped lines are joined, while blank lines,
    headings and list items provide paragraph boundaries.
    """

    paragraphs = []

    for document in documents:

        page_number = document["page"]
        lines = document["text"].splitlines()

        current_lines = []

        def save_current():
            if current_lines:
                paragraph_text = " ".join(current_lines).strip()

                if paragraph_text:
                    paragraphs.append({
                        "text": paragraph_text,
                        "page": page_number
                    })

                current_lines.clear()

        for line in lines:

            line = line.strip()

            if not line:
                save_current()
                continue

            if is_heading(line):
                save_current()

                paragraphs.append({
                    "text": line,
                    "page": page_number,
                    "is_heading": True
                })

                continue

            if is_list_item(line):
                save_current()

            current_lines.append(line)

        save_current()

    return paragraphs


def split_into_sentences(text):
    """Split text at likely sentence boundaries."""

    text = text.strip()

    if not text:
        return []

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def is_faq_section(heading):
    """Identify common FAQ and question-answer section headings."""

    heading = re.sub(
        r"[^a-z0-9\s]",
        " ",
        heading.lower()
    )

    heading = " ".join(heading.split())

    faq_patterns = [
        r"\bfaq\b",
        r"\bfaqs\b",
        r"\bfrequently asked questions\b",
        r"\bcommon questions\b",
        r"\bquestions and answers\b",
        r"\bq and a\b",
        r"\bq a\b",
    ]

    return any(
        re.search(pattern, heading)
        for pattern in faq_patterns
    )


def build_sections(paragraphs):
    """Group paragraphs under their detected section headings."""

    sections = []

    current_section = {
        "heading": "General",
        "paragraphs": []
    }

    for paragraph in paragraphs:

        if paragraph.get("is_heading"):

            if current_section["paragraphs"]:
                sections.append(current_section)

            current_section = {
                "heading": paragraph["text"],
                "paragraphs": []
            }

        else:
            current_section["paragraphs"].append(paragraph)

    if current_section["paragraphs"]:
        sections.append(current_section)

    return sections


def build_section_context(section):
    """
    Extract a short introductory sentence for the section.
    This context helps chunks remain meaningful independently.
    """

    for paragraph in section["paragraphs"]:

        text = paragraph["text"].strip()

        if is_list_item(text):
            continue

        sentences = split_into_sentences(text)

        if not sentences:
            continue

        context = sentences[0].strip()

        if len(context) > 250:
            context = context[:250].rsplit(" ", 1)[0]

        return context

    return ""


def split_long_text(text, max_size):
    """Split oversized text at sentence or word boundaries."""

    sentences = split_into_sentences(text)

    parts = []
    current = ""

    for sentence in sentences:

        if len(sentence) > max_size:

            if current:
                parts.append(current)
                current = ""

            words = sentence.split()
            word_part = ""

            for word in words:

                candidate = f"{word_part} {word}".strip()

                if len(candidate) > max_size and word_part:
                    parts.append(word_part)
                    word_part = word
                else:
                    word_part = candidate

            if word_part:
                parts.append(word_part)

        else:

            candidate = f"{current} {sentence}".strip()

            if len(candidate) <= max_size:
                current = candidate

            else:
                if current:
                    parts.append(current)

                current = sentence

    if current:
        parts.append(current)

    return parts


def is_service_start(text):
    """
    Identify numbered service headings inside the Services section.
    """

    return bool(
        re.match(r"^\d{1,2}[.)]\s+\S", text.strip())
    )


def extract_service_title(text):
    """Extract the service name from its numbered heading."""

    text = text.strip()

    match = re.match(
        r"^\d{1,2}[.)]\s+(.+)$",
        text
    )

    if not match:
        return text

    heading_content = match.group(1).strip()

    # The first full stop separates the service title
    # from its description in the source document.
    title_parts = re.split(
        r"\.\s+(?=[A-Z])",
        heading_content,
        maxsplit=1
    )

    title = title_parts[0].strip().rstrip(".")

    return title or heading_content


def build_service_blocks(paragraphs):
    """
    Group each numbered service heading with its description
    and following bullet points.

    Paragraphs before the first service heading are kept separately.
    """

    introductory_paragraphs = []
    service_blocks = []
    current_block = None

    for paragraph in paragraphs:

        text = paragraph["text"].strip()

        if is_service_start(text):

            if current_block:
                service_blocks.append(current_block)

            current_block = {
                "heading": paragraph,
                "paragraphs": []
            }

        elif current_block is not None:
            current_block["paragraphs"].append(paragraph)

        else:
            introductory_paragraphs.append(paragraph)

    if current_block:
        service_blocks.append(current_block)

    return introductory_paragraphs, service_blocks


def create_service_chunks(service_blocks, content_limit):
    """
    Create chunks that preserve complete service information.

    Complete services stay together whenever possible.
    An oversized service is split into smaller parts, with its
    original heading repeated in every part.
    """

    service_chunks = []

    for block in service_blocks:

        heading_text = block["heading"]["text"].strip()

        heading_page = block["heading"]["page"]

        body_paragraphs = block["paragraphs"]

        complete_body = "\n\n".join(
            paragraph["text"].strip()
            for paragraph in body_paragraphs
        )

        complete_text = heading_text

        if complete_body:
            complete_text += "\n\n" + complete_body

        all_pages = [
            block["heading"]["page"]
        ] + [
            paragraph["page"]
            for paragraph in body_paragraphs
        ]

        # Keep the entire service together if it fits.
        if len(complete_text) <= content_limit:

            service_chunks.append({
                "text": complete_text,
                "pages": all_pages
            })

            continue

        # Reserve space for repeating its heading.
        body_limit = content_limit - len(heading_text) - 2

        if body_limit <= 0:
            raise ValueError(
                "Service heading is too large for the configured chunk size."
            )

        body_units = []

        for paragraph in body_paragraphs:

            parts = split_long_text(
                paragraph["text"],
                body_limit
            )

            for part in parts:
                body_units.append({
                    "text": part,
                    "page": paragraph["page"]
                })

        current_parts = []
        current_length = len(heading_text)

        def save_service_part():

            if not current_parts:
                return

            content = "\n\n".join(
                item["text"]
                for item in current_parts
            )

            service_text = heading_text + "\n\n" + content

            pages = [heading_page] + [
                item["page"]
                for item in current_parts
            ]

            service_chunks.append({
                "text": service_text,
                "pages": pages
            })

        for unit in body_units:

            additional_length = len(unit["text"]) + 2

            if current_length + additional_length <= content_limit:

                current_parts.append(unit)
                current_length += additional_length

            else:

                save_service_part()

                current_parts = [unit]
                current_length = (
                    len(heading_text) +
                    2 +
                    len(unit["text"])
                )

        save_service_part()

        # Handle a service that contains only a heading.
        if not body_units:
            service_chunks.append({
                "text": heading_text,
                "pages": [heading_page]
            })

    return service_chunks


def chunk_service_section(
    section,
    heading_prefix,
    content_limit,
    section_context
):
    """
    Special chunking logic for the Services section.

    Creates:
    1. A compact service index.
    2. An introductory chunk, if present.
    3. Chunks containing complete service blocks.
    """

    introductory_paragraphs, service_blocks = build_service_blocks(
        section["paragraphs"]
    )

    output_chunks = []

    # Create a compact index from the actual service headings.
    service_names = [
        extract_service_title(block["heading"]["text"])
        for block in service_blocks
    ]

    if service_names:

        index_text = "Services offered:\n" + "\n".join(
            f"{index}. {name}"
            for index, name in enumerate(service_names, start=1)
        )

        if len(index_text) <= content_limit:

            output_chunks.append({
                "text": index_text,
                "pages": [
                    block["heading"]["page"]
                    for block in service_blocks
                ]
            })

    # Keep introductory information as its own chunk.
    if introductory_paragraphs:

        intro_text = "\n\n".join(
            paragraph["text"]
            for paragraph in introductory_paragraphs
        )

        intro_parts = split_long_text(
            intro_text,
            content_limit
        )

        for part in intro_parts:

            output_chunks.append({
                "text": part,
                "pages": [
                    paragraph["page"]
                    for paragraph in introductory_paragraphs
                ]
            })

    # Build complete service chunks.
    service_chunks = create_service_chunks(
        service_blocks,
        content_limit
    )

    output_chunks.extend(service_chunks)

    final_chunks = []

    for item in output_chunks:

        chunk_text = heading_prefix + item["text"]

        embedding_text = chunk_text

        if section_context:
            embedding_text = (
                f"Document section: {section['heading']}\n"
                f"Section overview: {section_context}\n\n"
                f"{chunk_text}"
            )

        final_chunks.append({
            "text": chunk_text,
            "embedding_text": embedding_text,
            "section": section["heading"],
            "page_start": min(item["pages"]),
            "page_end": max(item["pages"])
        })

    return final_chunks


def create_table_chunks(documents, chunk_size):
    """
    Convert detected table rows into descriptive, searchable chunks.

    Each data row retains its column headers so that values
    remain associated with the correct fields.
    """

    table_chunks = []

    for document in documents:

        page_number = document["page"]

        for table in document.get("tables", []):

            rows = table.get("rows", [])

            if len(rows) < 2:
                continue

            headers = [
                str(cell).strip()
                for cell in rows[0]
            ]

            headers = [
                header if header else f"Column {index + 1}"
                for index, header in enumerate(headers)
            ]

            table_title = " | ".join(headers)

            for row_number, row in enumerate(rows[1:], start=1):

                fields = []

                for index, value in enumerate(row):

                    value = str(value).strip()

                    if not value:
                        continue

                    header = (
                        headers[index]
                        if index < len(headers)
                        else f"Column {index + 1}"
                    )

                    fields.append(f"{header}: {value}")

                if not fields:
                    continue

                row_text = (
                    f"Table: {table_title}\n"
                    + "\n".join(fields)
                )

                parts = split_long_text(
                    row_text,
                    chunk_size
                )

                for part in parts:

                    table_chunks.append({
                        "text": part,
                        "embedding_text": (
                            f"Structured table information\n"
                            f"Table columns: {table_title}\n\n"
                            f"{part}"
                        ),
                        "section": f"Table: {table_title}",
                        "page_start": page_number,
                        "page_end": page_number,
                        "chunk_index": None
                    })

    return table_chunks


def chunk_faq_section(section, heading_prefix, content_limit):
    """
    Split FAQ sections into individual question-and-answer chunks.

    Each question is grouped with the sentences that follow it,
    until the next question begins.
    """

    faq_groups = []
    current_group = []
    current_page = None
    introductory_sentences = []

    for paragraph in section["paragraphs"]:

        sentences = split_into_sentences(
            paragraph["text"]
        )

        for sentence in sentences:

            sentence = sentence.strip()

            if not sentence:
                continue

            # A new question starts a new FAQ group.
            if sentence.endswith("?"):

                if current_group:
                    faq_groups.append({
                        "text": " ".join(current_group),
                        "page": current_page
                    })

                current_group = [sentence]
                current_page = paragraph["page"]

            elif current_group:

                # Add answer sentences to the current question.
                current_group.append(sentence)

            else:

                # Preserve introductory content before the first question.
                introductory_sentences.append({
                    "text": sentence,
                    "page": paragraph["page"]
                })

    if current_group:
        faq_groups.append({
            "text": " ".join(current_group),
            "page": current_page
        })

    # If no question boundaries were detected, use normal chunking.
    if not faq_groups:
        return None

    faq_chunks = []

    # Preserve any introductory content.
    if introductory_sentences:

        intro_text = " ".join(
            item["text"]
            for item in introductory_sentences
        )

        for part in split_long_text(
            intro_text,
            content_limit
        ):

            faq_chunks.append({
                "text": heading_prefix + part,
                "embedding_text": (
                    f"Document section: {section['heading']}\n\n"
                    f"{heading_prefix}{part}"
                ),
                "section": section["heading"],
                "page_start": min(
                    item["page"]
                    for item in introductory_sentences
                ),
                "page_end": max(
                    item["page"]
                    for item in introductory_sentences
                )
            })

    # Create a separate chunk for each question and answer.
    for group in faq_groups:

        parts = split_long_text(
            group["text"],
            content_limit
        )

        for part in parts:

            chunk_text = heading_prefix + part

            faq_chunks.append({
                "text": chunk_text,
                "embedding_text": (
                    f"Document section: {section['heading']}\n"
                    f"FAQ question and answer:\n\n"
                    f"{chunk_text}"
                ),
                "section": section["heading"],
                "page_start": group["page"],
                "page_end": group["page"]
            })

    return faq_chunks


def chunk_documents(documents, chunk_size=1200, overlap=150):
    """
    Create section-aware chunks with source page metadata.

    FAQ sections use question-and-answer-aware chunking.
    The Services section uses service-aware chunking.
    Other sections use paragraph-based chunking.
    Tables are converted into structured row chunks.

    chunk_size and overlap are measured in characters, not tokens.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be >= 0 and smaller than chunk_size."
        )

    paragraphs = extract_paragraphs(documents)
    sections = build_sections(paragraphs)

    chunks = []

    for section in sections:

        heading = section["heading"]
        section_context = build_section_context(section)

        heading_prefix = f"Section: {heading}\n\n"

        content_limit = chunk_size - len(heading_prefix)

        if content_limit <= 0:
            raise ValueError(
                "chunk_size is too small for the section heading."
            )

        # 1. Apply FAQ-aware chunking independently of Services.
        if is_faq_section(heading):

            faq_chunks = chunk_faq_section(
                section=section,
                heading_prefix=heading_prefix,
                content_limit=content_limit
            )

            if faq_chunks is not None:

                for chunk in faq_chunks:
                    chunk["chunk_index"] = len(chunks)
                    chunks.append(chunk)

                continue

        # 2. Apply service-aware chunking only to Services.
        if re.match(
            r"^\s*\d+[.)]\s*Services\s*$",
            heading,
            re.IGNORECASE
        ):

            service_chunks = chunk_service_section(
                section=section,
                heading_prefix=heading_prefix,
                content_limit=content_limit,
                section_context=section_context
            )

            for chunk in service_chunks:

                chunk["chunk_index"] = len(chunks)
                chunks.append(chunk)

            continue

        # 3. Original paragraph-based chunking for other sections.
        units = []

        for paragraph in section["paragraphs"]:

            parts = split_long_text(
                paragraph["text"],
                content_limit
            )

            for part in parts:
                units.append({
                    "text": part,
                    "page": paragraph["page"]
                })

        current_units = []
        current_length = 0

        def save_current():

            if not current_units:
                return

            content = "\n\n".join(
                item["text"]
                for item in current_units
            )

            pages = [
                item["page"]
                for item in current_units
            ]

            chunk_text = heading_prefix + content

            embedding_text = chunk_text

            if section_context:
                embedding_text = (
                    f"Document section: {heading}\n"
                    f"Section overview: {section_context}\n\n"
                    f"{chunk_text}"
                )

            chunks.append({
                "text": chunk_text,
                "embedding_text": embedding_text,
                "section": heading,
                "page_start": min(pages),
                "page_end": max(pages),
                "chunk_index": len(chunks)
            })

        for unit in units:

            unit_length = len(unit["text"])

            additional_length = (
                unit_length + (2 if current_units else 0)
            )

            if (
                current_length + additional_length
                <= content_limit
            ):

                current_units.append(unit)
                current_length += additional_length

            else:

                save_current()

                # Preserve complete previous units for overlap.
                overlap_units = []
                overlap_length = 0

                for previous in reversed(current_units):

                    previous_length = len(previous["text"]) + 2

                    if overlap_length + previous_length > overlap:
                        break

                    overlap_units.insert(0, previous)
                    overlap_length += previous_length

                current_units = overlap_units

                current_length = sum(
                    len(item["text"])
                    for item in current_units
                ) + max(0, len(current_units) - 1) * 2

                required = (
                    unit_length + (2 if current_units else 0)
                )

                if current_length + required > content_limit:
                    current_units = []
                    current_length = 0

                current_units.append(unit)
                current_length += (
                    unit_length +
                    (2 if len(current_units) > 1 else 0)
                )

        save_current()

    # 4. Add structured table chunks.
    table_chunks = create_table_chunks(
        documents,
        chunk_size
    )

    chunks.extend(table_chunks)

    # 5. Assign unique sequential chunk indexes.
    for index, chunk in enumerate(chunks):
        chunk["chunk_index"] = index

    return chunks
