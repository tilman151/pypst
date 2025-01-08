import pytest

from pypst import Document, SetRule
from pypst.content import Content


def test_empty_content():
    obj = Content()
    assert obj.render() == "#[]"


def test_nested_content():
    obj = Content(Content())
    assert obj.render() == "#[]"

    obj = Content(Content("Foo", context=True))
    assert obj.render() == "#context [Foo]"

    obj = Content(Content("Foo"), context=True)
    assert obj.render() == "#context [Foo]"


@pytest.mark.integration
def test_content_compile(test_compile):
    content = Content(
        [SetRule("text", {"fill": "red"}), "This is page #here().page()"], context=True
    )
    doc = Document([content])
    test_compile(doc)
