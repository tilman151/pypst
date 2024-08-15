import pytest
import typst

from pypst.figure import Figure
from pypst.document import Document, Import


def test_empty_document():
    document = Document(None)

    assert len(document.body) == 0
    assert document.render() == ""


def test_document(dummy_body):
    document = Document(dummy_body)
    assert document.render() == "#text(fill: red)[Hello, world!]"


def test_document_with_multiple_body_elements(dummy_body):
    document = Document(dummy_body)
    document.add("This is another text")
    document.add(dummy_body)
    assert document.render() == (
        "#text(fill: red)[Hello, world!]\n"
        "This is another text\n"
        "#text(fill: red)[Hello, world!]"
    )


def test_document_with_imports(dummy_body):
    document = Document(dummy_body)
    document.add_import("@preview/cetz:0.2.2")
    assert document.render() == (
        '#import "@preview/cetz:0.2.2"\n\n' "#text(fill: red)[Hello, world!]"
    )


@pytest.mark.integration
def test_compilation(dummy_body, tmp_path):
    document = Document(Figure(dummy_body, caption='"This is a caption"'))
    document.add_import("@preview/cetz:0.2.2")

    with open(tmp_path / "test.typ", mode="wt") as f:
        f.write(document.render())

    typst.compile(tmp_path / "test.typ")


class TestImport:
    def test_module_import(self):
        imp = Import("todo.typ")
        assert imp.render() == '#import "todo.typ"'

    def test_import_with_members(self):
        imp = Import("todo.typ", ["task", "todo"])
        assert imp.render() == '#import "todo.typ": task, todo'

    def test_import_in_quotes(self):
        imp = Import('"todo.typ"')
        assert imp.render() == '#import "todo.typ"'

    def test_faulty_import(self):
        imp = Import("todo.typ", ["*", "task"])
        with pytest.raises(ValueError):
            imp.render()
