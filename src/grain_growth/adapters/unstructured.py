# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mudit Choudhary
"""Unstructured → blocks.

    from unstructured.partition.pdf import partition_pdf
    from grain_growth import chunk_document
    from grain_growth.adapters.unstructured import from_unstructured

    elements = partition_pdf("paper.pdf", strategy="hi_res")
    chunks, skipped = chunk_document(from_unstructured(elements), filename="paper")

Unstructured is imported lazily — nothing here requires it to be installed.
"""

CATEGORY_TO_TYPE = {
    "Title": "section",           # Unstructured labels every heading "Title"
    "Header": "section",
    "NarrativeText": "paragraph",
    "UncategorizedText": "paragraph",
    "Text": "paragraph",
    "ListItem": "list",
    "FigureCaption": "caption",
    "Table": "table",
    "Formula": "formula",
    "Footer": "footnote",
}
DROPPED = {"PageBreak", "Image", "PageNumber", "Address", "EmailAddress"}


def from_unstructured(elements, title=None):
    """Blocks from a list of Unstructured elements, in reading order.

    Unstructured gives every heading the category "Title", so the document
    title cannot be told from a section heading. Pass `title=` to set one;
    otherwise the chunker falls back to the filename, which is what Anneal's
    evaluation did.
    """
    blocks = []
    if title:
        blocks.append({"type": "title", "page": 0, "text": title})
    for el in elements:
        category = getattr(el, "category", None) or type(el).__name__
        if category in DROPPED:
            continue
        text = (getattr(el, "text", "") or "").strip()
        if not text:
            continue
        page = getattr(getattr(el, "metadata", None), "page_number", None)
        blocks.append({"type": CATEGORY_TO_TYPE.get(category, "paragraph"),
                       "page": max(0, page - 1) if isinstance(page, int) else 0,
                       "text": text})
    return blocks
