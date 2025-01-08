import pytest

from pypst import Document, SetRule
from pypst.content import Content


@pytest.mark.parametrize(
    "obj,rendered",
    [
        (Content(), "#[]"),
        (Content("Foo", context=True), "#context [Foo]"),
        (
            Content([Content("Foo"), "This is a plain string."]),
            "#[\n  #[Foo]\n  This is a plain string.\n]",
        ),
    ],
)
def test_content(obj, rendered):
    assert obj.render() == rendered


@pytest.mark.parametrize(
    "obj,rendered",
    [
        (Content(Content()), "#[]"),
        (Content(Content("Foo", context=True)), "#context [Foo]"),
        (Content(Content("Foo"), context=True), "#context [Foo]"),
    ],
)
def test_nested_content(obj, rendered):
    assert obj.render() == rendered


@pytest.mark.integration
def test_content_compile(test_compile):
    content = Content(
        [SetRule("text", {"fill": "red"}), "This is page #here().page()"], context=True
    )
    doc = Document([content])
    test_compile(doc)
