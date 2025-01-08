import pytest

from pypst import Content, Document, SetRule


def test_set_rule():
    obj = SetRule(selector="text", arguments={"fill": "red", "size": "18pt"})
    assert obj.render() == "#set text(fill: red, size: 18pt)"


@pytest.mark.integration
def test_set_rule_compile(test_compile):
    obj = SetRule(selector="text", arguments={"fill": "red", "size": "18pt"})
    doc = Document([obj, Content("Large and red text.")])
    test_compile(doc)
