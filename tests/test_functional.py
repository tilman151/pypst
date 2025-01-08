import pytest

from pypst import Content, Document, Functional, Set


def test_empty_functional():
    obj = Functional()
    assert obj.render() == "#{}"


def test_nested_functional():
    obj = Functional(Functional())
    assert obj.render() == "#{}"

    obj = Functional(Functional("Foo", context=True))
    assert obj.render() == "#context {Foo}"

    obj = Functional(Functional("Foo"), context=True)
    assert obj.render() == "#context {Foo}"


@pytest.mark.integration
def test_functional_compile(test_compile):
    content = Functional(
        [Set("text", {"fill": "red"}), Content("This is page #here().page()")],
        context=True,
    )
    doc = Document([content])
    test_compile(doc)
