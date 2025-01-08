import pytest

from pypst import Content, Document, Set


def test_set():
    obj = Set(selector="text", arguments={"fill": "red", "size": "18pt"})
    assert obj.render() == "#set text(fill: red, size: 18pt)"


@pytest.mark.integration
def test_set_compile(test_compile):
    obj = Set(selector="text", arguments={"fill": "red", "size": "18pt"})
    doc = Document([obj, Content("Large and red text.")])
    test_compile(doc)
