import pytest

from pypst import Content, Document, Functional, Heading, ShowRule


def test_show_rule_no_arg():
    obj = ShowRule(selector="heading", body="text.with(fill: red)")
    assert obj.render() == "#show heading: text.with(fill: red)"


def test_show_rule():
    obj = ShowRule(selector="heading", argument="it", body="text(fill: red, it)")

    assert obj.render() == "#show heading: it => text(fill: red, it)"


def test_show_rule_functional():
    obj = ShowRule(
        selector="heading", argument="it", body=Functional(["v(0.5em)", "it"])
    )
    assert obj.render() == "#show heading: it => {\n  v(0.5em)\n  it\n}"


def test_show_rule_content():
    obj = ShowRule(
        selector="heading", argument="it", body=Content(["#v(0.5em)", "#it"])
    )
    assert obj.render() == "#show heading: it => [\n  #v(0.5em)\n  #it\n]"


@pytest.mark.integration
def test_show_rule_no_arg_compile(test_compile):
    rule = ShowRule(selector="heading", body="text.with(fill: red)")
    doc = Document([rule, Heading("[Without rule argument]")])
    test_compile(doc)


@pytest.mark.integration
def test_show_rule_compile(test_compile):
    rule = ShowRule(selector="heading", argument="it", body="text(fill: red, it)")
    doc = Document([rule, Heading("[With rule argument]")])
    test_compile(doc)
