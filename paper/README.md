# The paper

`paper.tex` — *Grain-Growth Chunking: Structure-Aware Segmentation for
Retrieval-Augmented Generation.* Fourteen pages, including the references and
Appendix A (round 1 results).

## Build

```bash
tectonic paper.tex          # self-contained, downloads what it needs
# or
latexmk -pdf paper.tex      # a normal TeX Live install
```

No external image files: every figure is TikZ or pgfplots, everything else is a table.

## Submission bundles

```bash
python make_submission.py     # tectonic on PATH, or TECTONIC=/path/to/tectonic
```

- `build/arxiv.tar.gz`: `paper.tex`, `paper.bbl` and `refs.bib`. Upload as is;
  it builds whether or not arXiv runs BibTeX.
- `build/anon/paper.pdf`: for double-blind review. Author, ORCID, commit id,
  repository names, links and the package name are removed, and the script
  refuses to finish if any of them survive in the PDF text or metadata. The
  method name and parser names stay, as is normal for double-blind venues.

## Before submitting

1. **Citations: checked 2026-09-22.** Every arXiv id against the arXiv API,
   every DOI and venue against Crossref, and every URL resolves. Only Holm
   (1979) could not be machine-checked: it is not in Crossref, and the entry
   matches the standard citation.
2. **Models: cited.** Questions by `gpt-oss-120b` (340) and `gpt-oss-20b` (60),
   answers by Qwen3 4B Instruct, scoring by `nli-deberta-v3-base` and Gemma 3 4B.
3. **Category.** `cs.IR` as primary, `cs.CL` as cross-list. A first submission
   to `cs.IR` will probably need an endorsement.
4. **Licence.** Consider arXiv's CC BY 4.0 so the text can be reused as freely
   as the code.

## Keeping it honest

Every number in the paper comes from `evals/Reports/Report.md` in the
[Anneal](https://github.com/mudit-choudhary/Anneal) repository, which is
regenerated from the raw per-question records. If a number changes there, it
must change here. The claims that the paper deliberately does *not* make —
that grain-growth beats a recursive character splitter, that chunk shape
*causes* the retrieval gain, that faithfulness was measured — are the ones to
protect in any revision. So is the pre-registration caveat in §4: the
repository went public after the run, so its timestamps are the author's own.
