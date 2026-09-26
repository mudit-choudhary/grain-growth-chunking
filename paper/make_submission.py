"""Build the two submission bundles from paper.tex and refs.bib.

    python make_submission.py        # tectonic on PATH, or set TECTONIC=/path/to/tectonic

build/arxiv/       paper.tex + paper.bbl + refs.bib, tarred as build/arxiv.tar.gz, with paper.pdf
build/anon/        the same paper with the author, self-citations and links removed,
                   for double-blind review; its PDF is build/anon/paper.pdf

Anonymisation is a list of exact replacements. If paper.tex changes so that one no
longer matches, the script stops rather than ship a copy that still names you.
"""
import os
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"
TECTONIC = os.environ.get("TECTONIC") or shutil.which("tectonic") or sys.exit("tectonic not found; set TECTONIC")

TEX_REPLACEMENTS = [
    (re.compile(r"\\author\{.*?\n\n", re.S), "\\author{Anonymous authors}\n\n"),
    (re.compile(r" \(commit \\code\{[0-9a-f]+\}\)"), ""),
    (re.compile(r"published separately, as \\code\{textreflow\}"), "published separately"),
    (re.compile(r"\\section\{Availability\}.*?\\end\{sloppypar\}\n", re.S),
     "\\section{Availability}\n\nThe library, the evaluation harness, the pre-registration, the amendment\n"
     "log, the frozen question set and the per-question records are public and\n"
     "archived with a DOI. Links are withheld for review~\\cite{grain_growth_software,anneal}.\n"),
]
ANON_BIB_KEYS = {
    "grain_growth_software": "Chunking library, version 1.0.0",
    "textreflow_software": "Reading-order and paragraph assembler, version 1.0.0",
    "recrystal_software": "Layout parser, version 1.0.0",
    "anneal": "Evaluation harness, pre-registration and per-question records",
}
# Anything left matching these means the anonymised copy still identifies the author.
LEAKS = re.compile(r"Choudhary|orcid|mudit|zenodo|github\.com|bdad126|\bAnneal\b|pip install", re.I)


def compile_tex(folder):
    subprocess.run([TECTONIC, "-X", "compile", "--keep-intermediates", "paper.tex"],
                   cwd=folder, check=True, capture_output=True)


def anonymise_tex(text):
    for pattern, repl in TEX_REPLACEMENTS:
        text, n = pattern.subn(lambda _: repl, text)
        if n != 1:
            sys.exit(f"anonymise: expected 1 match for {pattern.pattern!r}, found {n}")
    return text


def anonymise_bib(text):
    for key, what in ANON_BIB_KEYS.items():
        text, n = re.subn(r"@misc\{" + key + r",.*?\n\}\n",
                          lambda _: f"@misc{{{key},\n  title  = {{{what}}},\n  author = {{Anonymous}},\n"
                                    f"  year   = {{2026}},\n  note   = {{Withheld for review}}\n}}\n",
                          text, flags=re.S)
        if n != 1:
            sys.exit(f"anonymise: bib entry {key} not found exactly once")
    return text


def main():
    shutil.rmtree(BUILD, ignore_errors=True)
    arxiv, anon = BUILD / "arxiv", BUILD / "anon"
    for d in (arxiv, anon):
        d.mkdir(parents=True)

    shutil.copy(HERE / "paper.tex", arxiv)
    shutil.copy(HERE / "refs.bib", arxiv)
    compile_tex(arxiv)
    with tarfile.open(BUILD / "arxiv.tar.gz", "w:gz") as tar:
        for name in ("paper.tex", "paper.bbl", "refs.bib"):   # .bbl and .bib, so it builds with or without BibTeX
            tar.add(arxiv / name, arcname=name)

    (anon / "paper.tex").write_text(anonymise_tex((HERE / "paper.tex").read_text()))
    (anon / "refs.bib").write_text(anonymise_bib((HERE / "refs.bib").read_text()))
    compile_tex(anon)
    shown = subprocess.run(["pdftotext", str(anon / "paper.pdf"), "-"], capture_output=True, text=True).stdout
    meta = subprocess.run(["pdfinfo", str(anon / "paper.pdf")], capture_output=True, text=True).stdout
    leaks = sorted(set(LEAKS.findall(shown + meta)))
    if leaks:
        sys.exit(f"anonymised PDF still contains: {leaks}")

    print(f"arXiv bundle: {BUILD / 'arxiv.tar.gz'}")
    print(f"anonymised:   {anon / 'paper.pdf'} (checked: no author, links or commit ids)")


if __name__ == "__main__":
    main()
