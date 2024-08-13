import pytest
import typst

from pypst.enumerate import Enumerate


def test_add():
    enum = Enumerate(["First item", "Second item", "Third item"])
    enum.add("Fourth item")

    assert len(enum.elements) == 4
    assert enum.elements[-1] == "Fourth item"


def test_simple_enum():
    enum = Enumerate(["First item", "Second item", "Third item"])
    assert enum.render() == "+ First item\n+ Second item\n+ Third item"


def test_simple_nested_enum():
    enum = Enumerate(
        ["First item", Enumerate(["Nested item 1", "Nested item 2"]), "Second item"]
    )
    assert (
        enum.render()
        == "+ First item\n  + Nested item 1\n  + Nested item 2\n+ Second item"
    )


def test_functional_nested_enum():
    enum = Enumerate(
        ["First item", Enumerate(["Nested item 1", "Nested item 2"]), "Second item"],
        indent="1em",
    )
    assert (
        enum.render() == "#enum(\n  indent: 1em,\n  "
        "[First item],\n  "
        "[\n  + Nested item 1\n  + Nested item 2\n  ],\n  "
        "[Second item]\n)"
    )


def test_enum_with_tight():
    enum = Enumerate(["First item", "Second item", "Third item"], tight=True)
    assert (
        enum.render() == "#enum(\n  tight: true,\n"
        "  [First item],\n  [Second item],\n  [Third item]\n)"
    )


def test_enum_with_numbering():
    enum = Enumerate(["First item", "Second item", "Third item"], numbering='"1.1"')
    assert (
        enum.render() == '#enum(\n  numbering: "1.1",\n'
        "  [First item],\n  [Second item],\n  [Third item]\n)"
    )


def test_enum_with_start():
    enum = Enumerate(["First item", "Second item", "Third item"], start=2)
    assert (
        enum.render() == "#enum(\n  start: 2,\n"
        "  [First item],\n  [Second item],\n  [Third item]\n)"
    )


def test_enum_with_full():
    enum = Enumerate(["First item", "Second item", "Third item"], full=True)
    assert (
        enum.render() == "#enum(\n  full: true,\n"
        "  [First item],\n  [Second item],\n  [Third item]\n)"
    )


def test_enum_with_indent():
    enum = Enumerate(["First item", "Second item", "Third item"], indent="1em")
    assert (
        enum.render() == "#enum(\n  indent: 1em,\n"
        "  [First item],\n  [Second item],\n  [Third item]\n)"
    )


def test_enum_with_body_indent():
    enum = Enumerate(["First item", "Second item", "Third item"], body_indent="1em")
    assert (
        enum.render() == "#enum(\n  body-indent: 1em,\n"
        "  [First item],\n  [Second item],\n  [Third item]\n)"
    )


def test_enum_with_spacing():
    enum = Enumerate(["First item", "Second item", "Third item"], spacing="1em")
    assert (
        enum.render() == "#enum(\n  spacing: 1em,\n"
        "  [First item],\n  [Second item],\n  [Third item]\n)"
    )


def test_with_number_align():
    enum = Enumerate(["First item", "Second item", "Third item"], number_align="right")
    assert (
        enum.render() == "#enum(\n  number-align: right,\n"
        "  [First item],\n  [Second item],\n  [Third item]\n)"
    )


@pytest.mark.integration
@pytest.mark.parametrize(
    "enum",
    [
        Enumerate(
            [
                "First item",
                Enumerate(["Nested item 1", "Nested item 2"]),
                "Second item",
            ]
        ),
        Enumerate(
            [
                "First item",
                Enumerate(["Nested item 1", "Nested item 2"]),
                "Second item",
            ],
            tight=True,
        ),
        Enumerate(
            ["First item", "Second item", "Third item"],
            numbering='"1.1"',
            start=2,
            full=True,
        ),
    ],
)
def test_compilation(enum, tmp_path):
    with open(tmp_path / "test.typ", mode="wt") as f:
        f.write(enum.render())

    typst.compile(tmp_path / "test.typ")
