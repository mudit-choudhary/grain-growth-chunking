# Grain-Growth Chunking

Structure-aware chunking for retrieval. A chunk grows by accepting the next
block whole and keeps growing until it reaches the size budget **or meets a
barrier** — a section heading, or a block that must stand alone such as a
table. Barriers are absolute: a chunk never crosses one, however much budget is
left.

The name is from metallurgy. In annealing, grains nucleate and grow outward
until they meet a boundary; here a chunk nucleates at a section heading and
grows through the prose until the document's own structure stops it.

- **No dependencies.** Standard library only — `json`, `re`, `pathlib`.
- **No parser required.** It consumes typed blocks, so any parser can feed it.
  Adapters for Docling and Unstructured are included.
- **Measured, not asserted.** See [Evidence](#evidence), including what was
  *not* established.

```bash
pip install grain-growth-chunking
```

## Use

```python
from grain_growth import chunk_document

blocks = [
    {"type": "title",     "page": 0, "text": "Attention Is All You Need"},
    {"type": "section",   "page": 2, "text": "3 Model Architecture"},
    {"type": "paragraph", "page": 2, "text": "Most competitive neural sequence …"},
    {"type": "table",     "page": 3, "text": "| Layer | Complexity |\n| --- | --- |"},
]

chunks, skipped = chunk_document(blocks, filename="attention")

chunks[0]["text"]      # heading path + body — this is what you embed
chunks[0]["body"]      # body only
chunks[0]["metadata"]  # filename, title, section, page_start, page_end,
                       # block_types, chunk_index, n_chars
skipped                # authors and footnotes, deliberately not embedded
```

Sizes are in characters of body text: `target_chars=1500` is the packing
budget, `max_chars=2000` the point at which a single oversized block is split
at sentence boundaries with a one-sentence overlap. The defaults suit a
512-token embedding model; raise both together for a larger window.

## The input contract

The algorithm never sees a PDF. It consumes an ordered list of typed blocks:

```python
{"type": "paragraph", "page": 2, "text": "We train the model on …"}
```

| `type` | Treated as |
|---|---|
| `title` | the document title; prefixed to every chunk's embedded text |
| `section` | a heading — a barrier; never a chunk of its own |
| `paragraph` | prose, packed whole up to the budget |
| `list` | packed like prose, split at item boundaries |
| `caption` | stands alone, or travels with an adjacent table |
| `table` | stands alone, fenced |
| `formula` | fenced, but stays packed with the prose that explains it |
| `footnote`, `authors` | excluded from embedding, returned as `skipped` |

Order matters: blocks must be in reading order, because chunks grow along it.
`page` is 0-based and only feeds the `page_start`/`page_end` metadata.

Check your blocks before trusting the output — a mislabelled block does not
crash anything, it quietly produces worse chunks:

```python
from grain_growth import validate_blocks
validate_blocks(blocks)                 # raises ValueError on the first problem
validate_blocks(blocks, strict=False)   # or returns them all as strings
```

## From an existing parser

```python
from docling.document_converter import DocumentConverter
from grain_growth.adapters.docling import from_docling

doc = DocumentConverter().convert("paper.pdf").document
chunks, _ = chunk_document(from_docling(doc), filename="paper")
```

```python
from unstructured.partition.pdf import partition_pdf
from grain_growth.adapters.unstructured import from_unstructured

elements = partition_pdf("paper.pdf", strategy="hi_res")
chunks, _ = chunk_document(from_unstructured(elements, title="A Paper"), filename="paper")
```

Neither parser is a dependency; the adapters only read attributes. Writing your
own is a dict per block — that is the whole interface.

## What it does to prose

Three things a character-count splitter cannot do, because it cannot see
structure:

1. **A heading is a wall.** Two sections never share a chunk, so a retrieved
   chunk always belongs to one part of the argument.
2. **Tables and equations stay whole,** and are fenced (` ~~~table `) so the
   embedding model and the reader can both tell them from prose. A caption
   beside a table travels with it.
3. **Paragraphs are packed whole.** Only a paragraph that alone exceeds
   `max_chars` is split, and then at a sentence boundary with one sentence of
   overlap — never mid-sentence.

In bin-packing terms the packing is **next-fit**: when a block will not fit the
chunk being grown, that chunk is closed for good and a new one opens. No
earlier chunk is ever reopened. One pass, in order, which is what keeps reading
order intact.

In the published taxonomy this is document-based / structure-aware chunking;
the closest existing implementation is Unstructured's `by_title` chunker.

## Evidence

Developed and measured in [Anneal](https://github.com/muditchoudhary/anneal), a
local-first RAG pipeline. The
[evaluation](https://github.com/muditchoudhary/anneal/blob/main/evals/Reports/Report.md)
is pre-registered: metrics, tests and thresholds were fixed in writing before
the run — 3 parsers × 3 chunkers, 400 questions over a 514-paper corpus, every
comparison paired and corrected for multiplicity.

- **Beats a fixed-token window** on retrieval quality.
- **Against a stock recursive character splitter, the difference is _not
  established_.** It did not clear its pre-set threshold. The honest summary is
  that grain-growth matches it on the measured retrieval metrics while keeping
  tables, equations and section boundaries intact — properties the evaluation
  did not have a metric for.

If your documents have little structure — plain prose, no headings, no tables —
a recursive splitter will serve you just as well and is simpler. This library
earns its place on papers, reports, specifications and manuals.

## Versioning

`1.0.0` is the algorithm exactly as evaluated: `chunker.py` is the module from
the Anneal repository at the time of the report, unchanged apart from a licence
header, and the 36 tests that covered it there run here unchanged. Both
versions were checked to produce identical chunks on the same input. Anything
that would move a chunk boundary gets a major version, so a stored index stays
reproducible.

## Development

```bash
pip install -e ".[test]"
pytest -q                      # 46 tests, no network, no parser needed
```

## Citing

If this is useful in your work, please cite it — `CITATION.cff` in this
repository gives GitHub's "Cite this repository" button everything it needs:

> Choudhary, M. (2026). *Grain-Growth Chunking: structure-aware document
> chunking for retrieval* (version 1.0.0) [Software].
> https://github.com/muditchoudhary/grain-growth-chunking

The method and its measured results are in the
[evaluation report](https://github.com/muditchoudhary/anneal/blob/main/evals/Reports/Report.md).

## Licence

Apache-2.0 — use it commercially, modify it, ship it closed-source. It carries
an express patent grant from every contributor, which MIT does not, so adopting
it needs no legal guesswork about patents. Keep the notices; that is the whole
obligation.

(Anneal itself is AGPL, because it links PyMuPDF. That does not reach this
package, which depends on nothing.)
