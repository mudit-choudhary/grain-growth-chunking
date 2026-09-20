# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mudit Choudhary
"""Grain-Growth Chunking — structure-aware chunking for retrieval.

A chunk grows by accepting the next block whole and keeps growing until it
reaches the size budget or meets a barrier: a section heading, or a block that
must stand alone such as a table. Barriers are absolute — a chunk never crosses
one, however much budget is left.

    from grain_growth import chunk_document

    blocks = [{"type": "section", "page": 2, "text": "3 Method"},
              {"type": "paragraph", "page": 2, "text": "We train …"}]
    chunks, skipped = chunk_document(blocks, filename="paper")

`grain_growth.blocks` documents the input contract; `grain_growth.adapters`
turns Docling or Unstructured output into it.
"""

from .blocks import BLOCK_TYPES, validate_blocks
# The public surface. Everything else in .chunker is underscored and may
# change; these names are what the tests and downstream users rely on.
from .chunker import (
    DEFAULT_MAX_CHARS,
    DEFAULT_TARGET_CHARS,
    FENCE_CHAR,
    FENCED_INLINE,
    FENCED_STANDALONE,
    FENCED_TYPES,
    FORMULA_LEAD_SENTENCES,
    MIN_FORMULA_CHARS,
    SKIP_TYPES,
    STANDALONE_TYPES,
    bind_formula_groups,
    chunk_document,
    chunk_file,
    ends_cleanly,
    fence,
    fences_balanced,
    has_fence,
    load_blocks,
    split_long_text,
    split_sentences,
    starts_cleanly,
    starts_inside_fence,
    strip_fences,
)

__version__ = "1.0.0"

__all__ = [
    "BLOCK_TYPES", "DEFAULT_MAX_CHARS", "DEFAULT_TARGET_CHARS", "FENCE_CHAR",
    "FENCED_INLINE", "FENCED_STANDALONE", "FENCED_TYPES", "FORMULA_LEAD_SENTENCES",
    "MIN_FORMULA_CHARS", "SKIP_TYPES", "STANDALONE_TYPES", "bind_formula_groups",
    "chunk_document", "chunk_file", "ends_cleanly", "fence", "fences_balanced",
    "has_fence", "load_blocks", "split_long_text", "split_sentences", "starts_cleanly",
    "starts_inside_fence", "strip_fences", "validate_blocks", "__version__",
]
