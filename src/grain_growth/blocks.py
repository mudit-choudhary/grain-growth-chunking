# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mudit Choudhary
"""The input contract.

Grain-Growth Chunking consumes *typed blocks* — a document already reduced to
an ordered list of labelled pieces. Any parser can produce them; the algorithm
never sees a PDF. A block is a plain dict:

    {"type": "paragraph", "page": 2, "text": "We train the model on …"}

`type` is one of BLOCK_TYPES, `page` is a 0-based page number (used only for
the `page_start`/`page_end` metadata) and `text` is the plain text of the
piece, with intra-block line wrapping already resolved.

Order matters: blocks must be in reading order, since chunks grow along it.
"""

BLOCK_TYPES = frozenset({
    "title",      # the document title; prefixed to every chunk's embedded text
    "section",    # a heading: a barrier, never chunked on its own
    "paragraph",  # prose; packed up to the size budget
    "list",       # packed like prose, split at item boundaries
    "caption",    # stands alone, or travels with an adjacent table
    "table",      # stands alone, fenced
    "formula",    # fenced, but stays packed with the prose around it
    "footnote",   # excluded from embedding, returned as skipped
    "authors",    # excluded from embedding, returned as skipped
})


def validate_blocks(blocks, *, strict=True):
    """Check a block list against the contract.

    Returns the list of problems as strings. With `strict` (the default) the
    first problem raises ValueError instead — a mislabelled block does not
    crash the chunker, it quietly produces worse chunks, which is harder to
    notice than a failure here.
    """
    problems = []
    if not isinstance(blocks, (list, tuple)):
        problems.append(f"blocks must be a list, got {type(blocks).__name__}")
        blocks = []
    for i, b in enumerate(blocks):
        where = f"block {i}"
        if not isinstance(b, dict):
            problems.append(f"{where}: must be a dict, got {type(b).__name__}")
            continue
        kind = b.get("type")
        if kind not in BLOCK_TYPES:
            problems.append(f"{where}: type {kind!r} is not one of {sorted(BLOCK_TYPES)}")
        text = b.get("text")
        if text is not None and not isinstance(text, str):
            problems.append(f"{where}: text must be a string or None, got {type(text).__name__}")
        page = b.get("page", 0)
        if not isinstance(page, int) or isinstance(page, bool) or page < 0:
            problems.append(f"{where}: page must be a non-negative integer, got {page!r}")
    if problems and strict:
        raise ValueError("invalid blocks — " + "; ".join(problems[:5]))
    return problems
