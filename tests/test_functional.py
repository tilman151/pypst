import pytest

from pypst import Content, Document, Functional, SetRule


@pytest.mark.parametrize(
    "obj,rendered",
    [
        (Functional(), "#{}"),
        (Functional("Foo", context=True), "#context {Foo}"),
        (
            Functional([Content("Foo"), "This is a plain string."]),
            "#{\n  [Foo]\n  This is a plain string.\n}",
        ),
    ],
)
def test_functional(obj, rendered):
    assert obj.render() == rendered


@pytest.mark.parametrize(
    "obj,rendered",
    [
        (Functional(Functional()), "#{}"),
        (Functional(Functional("Foo", context=True)), "#context {Foo}"),
        (Functional(Functional("Foo"), context=True), "#context {Foo}"),
    ],
)
def test_nested_functional(obj, rendered):
    assert obj.render() == rendered


@pytest.mark.integration
def test_functional_compile(test_compile):
    content = Functional(
        [SetRule("text", {"fill": "red"}), Content("This is page #here().page()")],
        context=True,
    )
    doc = Document([content])
    test_compile(doc)
