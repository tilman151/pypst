import pytest

from pypst import Document, Heading, Show


def test_show_rule_no_arg():
    obj = Show(selector="heading", body="text.with(fill: red)")
    assert obj.render() == "#show heading: text.with(fill: red)"


def test_show_rule():
    obj = Show(selector="heading", argument="it", body="text(fill: red, it)")

    assert obj.render() == "#show heading: it => text(fill: red, it)"


@pytest.mark.integration
def test_show_rule_no_arg_compile(test_compile):
    rule = Show(selector="heading", body="text.with(fill: red)")
    doc = Document([rule, Heading("[Without rule argument]")])
    test_compile(doc)


@pytest.mark.integration
def test_show_rule_compile(test_compile):
    rule = Show(selector="heading", argument="it", body="text(fill: red, it)")
    doc = Document([rule, Heading("[With rule argument]")])
    test_compile(doc)
