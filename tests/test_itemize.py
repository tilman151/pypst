import pytest
import typst

from pypst.itemize import Itemize, Enumerate


def test_add():
    itemize = Itemize(["First item", "Second item", "Third item"])
    itemize.add("Fourth item")

    assert len(itemize.elements) == 4
    assert itemize.elements[-1] == "Fourth item"


def test_simple_list():
    itemize = Itemize(["First item", "Second item", "Third item"])
    assert itemize.render() == "- First item\n- Second item\n- Third item"


def test_simple_nested_list():
    itemize = Itemize(
        ["First item", Itemize(["Nested item 1", "Nested item 2"]), "Second item"]
    )
    assert (
        itemize.render()
        == "- First item\n  - Nested item 1\n  - Nested item 2\n- Second item"
    )


def test_simple_nested_with_enum():
    itemize = Itemize(
        ["First item", Enumerate(["Nested item 1", "Nested item 2"]), "Second item"]
    )
    assert (
        itemize.render()
        == "- First item\n  + Nested item 1\n  + Nested item 2\n- Second item"
    )


def test_functional_nested_list():
    itemize = Itemize(
        ["First item", Itemize(["Nested item 1", "Nested item 2"]), "Second item"],
        indent="1em",
    )
    assert (
        itemize.render() == "#list(\n  indent: 1em,\n  "
        "[First item],\n  "
        "[\n  - Nested item 1\n  - Nested item 2\n  ],\n  "
        "[Second item]\n)"
    )


def test_list_with_tight():
    itemize = Itemize(["First item", "Second item", "Third item"], tight=True)
    assert (
        itemize.render() == "#list(\n  tight: true,\n"
        "  [First item],\n  [Second item],\n  [Third item]\n)"
    )


def test_list_with_marker():
    itemize = Itemize(
        ["First item", "Second item", "Third item"], marker=['"*"', '"-"']
    )
    assert (
        itemize.render() == '#list(\n  marker: ("*", "-"),\n'
        "  [First item],\n  [Second item],\n  [Third item]\n)"
    )


def test_list_with_indent():
    itemize = Itemize(["First item", "Second item", "Third item"], indent="1em")
    assert (
        itemize.render() == "#list(\n  indent: 1em,\n"
        "  [First item],\n  [Second item],\n  [Third item]\n)"
    )


def test_list_with_body_indent():
    itemize = Itemize(["First item", "Second item", "Third item"], body_indent="1em")
    assert (
        itemize.render() == "#list(\n  body-indent: 1em,\n"
        "  [First item],\n  [Second item],\n  [Third item]\n)"
    )


def test_list_with_spacing():
    itemize = Itemize(["First item", "Second item", "Third item"], spacing="1em")
    assert (
        itemize.render() == "#list(\n  spacing: 1em,\n"
        "  [First item],\n  [Second item],\n  [Third item]\n)"
    )


@pytest.mark.integration
@pytest.mark.parametrize(
    "itemize",
    [
        Itemize(
            [
                "First item",
                Itemize(["Nested item 1", "Nested item 2"]),
                "Second item",
            ]
        ),
        Itemize(
            [
                "First item",
                Itemize(["Nested item 1", "Nested item 2"]),
                "Second item",
            ],
            tight=True,
        ),
        Itemize(
            ["First item", "Second item", "Third item"],
            marker=['"*"', '"-"'],
        ),
        Itemize(
            ["First item", "Second item", "Third item"],
            marker=["[--]", "[-]"],
        ),
        Itemize(
            ["First item", "Second item", "Third item"],
            tight=True,
            marker='"*"',
            indent="1em",
            body_indent="1em",
            spacing="1em",
        ),
    ],
)
def test_compilation(itemize, tmp_path):
    with open(tmp_path / "test.typ", mode="wt") as f:
        f.write(itemize.render())

    typst.compile(tmp_path / "test.typ")
