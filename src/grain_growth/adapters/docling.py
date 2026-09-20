# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mudit Choudhary
"""Docling → blocks.

Docling is imported lazily and only for type labels, so this package keeps its
promise of depending on nothing: `pip install grain-growth-chunking` pulls in
no parser at all.

    from docling.document_converter import DocumentConverter
    from grain_growth import chunk_document
    from grain_growth.adapters.docling import from_docling

    doc = DocumentConverter().convert("paper.pdf").document
    chunks, skipped = chunk_document(from_docling(doc), filename="paper")

The label mapping is the one used in Anneal's published evaluation, where
Docling was one of the three parsers compared.
"""

# Docling labels that carry document structure. Anything unlisted is prose if
# it has text at all; page furniture is dropped.
LABEL_TO_TYPE = {
    "title": "title",
    "section_header": "section",
    "text": "paragraph",
    "paragraph": "paragraph",
    "code": "paragraph",
    "key_value_region": "paragraph",
    "form": "paragraph",
    "checkbox_selected": "paragraph",
    "checkbox_unselected": "paragraph",
    "list_item": "list",
    "reference": "list",
    "caption": "caption",
    "table": "table",
    "document_index": "table",
    "formula": "formula",
    "footnote": "footnote",
}
DROPPED = {"page_header", "page_footer", "picture"}


def _label(item):
    return str(getattr(item, "label", "")).split(".")[-1].lower()


def _page(item):
    prov = getattr(item, "prov", None)
    if prov:
        page_no = getattr(prov[0], "page_no", None)
        if isinstance(page_no, int):
            return max(0, page_no - 1)          # Docling counts from 1
    return 0


def _text(item):
    for attr in ("text", "orig"):
        value = getattr(item, attr, None)
        if isinstance(value, str) and value.strip():
            return value.strip()
    export = getattr(item, "export_to_markdown", None)   # tables
    if callable(export):
        try:
            value = export()
        except Exception:                                # noqa: BLE001 - never fail a conversion
            return ""
        if isinstance(value, str):
            return value.strip()
    return ""


def from_docling(document):
    """Blocks from a `DoclingDocument`, in reading order."""
    items = getattr(document, "texts", None)
    if items is None:
        items = list(getattr(document, "iterate_items", lambda: [])())
        items = [i[0] if isinstance(i, tuple) else i for i in items]
    else:
        items = list(items) + list(getattr(document, "tables", []))

    blocks = []
    for item in items:
        label = _label(item)
        if label in DROPPED:
            continue
        text = _text(item)
        if not text:
            continue
        blocks.append({"type": LABEL_TO_TYPE.get(label, "paragraph"),
                       "page": _page(item), "text": text})
    blocks.sort(key=lambda b: b["page"])         # stable: reading order within a page is kept
    return blocks
