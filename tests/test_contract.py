"""The input contract and the parser adapters.

The adapters are tested against stand-ins rather than the real parsers: this
package must install and test with no parser present at all.
"""

import pytest

from grain_growth import BLOCK_TYPES, chunk_document, validate_blocks
from grain_growth.adapters.docling import from_docling
from grain_growth.adapters.unstructured import from_unstructured


class TestValidate:
    def test_good_blocks_pass(self):
        blocks = [{"type": "title", "page": 0, "text": "A Paper"},
                  {"type": "paragraph", "page": 1, "text": "Body."}]
        assert validate_blocks(blocks) == []

    def test_a_misspelled_type_is_caught(self):
        # The chunker would treat "heading" as prose and silently lose the
        # barrier, which is far harder to notice than an exception.
        with pytest.raises(ValueError, match="heading"):
            validate_blocks([{"type": "heading", "page": 0, "text": "3 Method"}])

    def test_collects_every_problem_when_not_strict(self):
        problems = validate_blocks(
            [{"type": "nope", "page": 0, "text": "x"},
             {"type": "paragraph", "page": -1, "text": "y"},
             {"type": "paragraph", "page": 0, "text": 5}], strict=False)
        assert len(problems) == 3

    def test_every_documented_type_is_accepted(self):
        blocks = [{"type": t, "page": 0, "text": "x"} for t in sorted(BLOCK_TYPES)]
        assert validate_blocks(blocks) == []


class _Prov:
    def __init__(self, page_no):
        self.page_no = page_no


class _Item:
    def __init__(self, label, text, page=1):
        self.label = f"DocItemLabel.{label.upper()}"
        self.text = text
        self.prov = [_Prov(page)]


class _Doc:
    def __init__(self, texts, tables=()):
        self.texts = texts
        self.tables = list(tables)


class TestDoclingAdapter:
    def test_labels_map_and_pages_become_zero_based(self):
        doc = _Doc([_Item("title", "A Paper", 1),
                    _Item("section_header", "3 Method", 2),
                    _Item("text", "We train the model.", 2),
                    _Item("list_item", "first point", 2),
                    _Item("formula", "E = mc^2", 3),
                    _Item("footnote", "see appendix", 3)])
        blocks = from_docling(doc)
        assert [b["type"] for b in blocks] == [
            "title", "section", "paragraph", "list", "formula", "footnote"]
        assert [b["page"] for b in blocks] == [0, 1, 1, 1, 2, 2]
        assert validate_blocks(blocks) == []

    def test_page_furniture_and_empty_items_are_dropped(self):
        doc = _Doc([_Item("page_header", "Preprint"), _Item("picture", ""),
                    _Item("text", "   "), _Item("text", "Real prose.")])
        assert [b["text"] for b in from_docling(doc)] == ["Real prose."]

    def test_unknown_labels_fall_back_to_prose(self):
        assert from_docling(_Doc([_Item("something_new", "text here")]))[0]["type"] == "paragraph"

    def test_output_chunks(self):
        doc = _Doc([_Item("title", "A Paper", 1), _Item("text", "Body sentence.", 1)])
        chunks, _ = chunk_document(from_docling(doc), filename="a_paper")
        assert chunks and chunks[0]["text"].startswith("A Paper")


class _El:
    def __init__(self, category, text, page=1):
        self.category = category
        self.text = text
        self.metadata = type("M", (), {"page_number": page})()


class TestUnstructuredAdapter:
    def test_categories_map(self):
        blocks = from_unstructured([_El("Title", "3 Method"),
                                    _El("NarrativeText", "We train the model."),
                                    _El("ListItem", "first point"),
                                    _El("Table", "| a | b |"),
                                    _El("PageBreak", "")],
                                   title="A Paper")
        assert [b["type"] for b in blocks] == [
            "title", "section", "paragraph", "list", "table"]
        assert blocks[0]["text"] == "A Paper"
        assert validate_blocks(blocks) == []

    def test_without_a_title_every_heading_stays_a_section(self):
        # Unstructured cannot tell a document title from a heading.
        blocks = from_unstructured([_El("Title", "3 Method")])
        assert [b["type"] for b in blocks] == ["section"]
