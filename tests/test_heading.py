import pytest
import typst

from pypst.heading import Heading


@pytest.mark.parametrize("body", ['"Hello"', "Hello"])
def test_simple_heading(body):
    assert Heading(body, level=1).render() == "= Hello"


def test_simple_heading_with_code_body():
    assert Heading("#emph[Hello]", level=1).render() == "= #emph[Hello]"


def test_function_heading_with_code_body():
    assert (
        Heading("#emph[Hello]", depth=2).render() == "#heading(emph[Hello], depth: 2)"
    )


def test_heading_with_depth():
    assert Heading('"Hello"', depth=2).render() == '#heading("Hello", depth: 2)'


def test_heading_with_offset():
    assert Heading('"Hello"', offset=2).render() == '#heading("Hello", offset: 2)'


def test_heading_with_numbering():
    assert (
        Heading('"Hello"', numbering='"1.1"').render()
        == '#heading("Hello", numbering: "1.1")'
    )


def test_heading_with_supplement():
    assert (
        Heading('"Hello"', supplement='"World"').render()
        == '#heading("Hello", supplement: "World")'
    )


def test_heading_with_outlined():
    assert (
        Heading('"Hello"', outlined=True).render()
        == '#heading("Hello", outlined: true)'
    )


def test_heading_with_bookmarked():
    assert (
        Heading('"Hello"', bookmarked=True).render()
        == '#heading("Hello", bookmarked: true)'
    )


@pytest.mark.integration
@pytest.mark.parametrize(
    "heading",
    [
        Heading('"Hello"', level=1, numbering='"1.1"'),
        Heading('"Hello"', level=2),
        Heading('"Hello"', supplement='"World"'),
        Heading('"Hello"', outlined=True),
        Heading('"Hello"', bookmarked=True),
        Heading('"Hello"', outlined=True),
        Heading("#emph[Hello]", level=1),
        Heading("#emph[Hello]", depth=1),
    ],
)
def test_compilation(heading, tmp_path):
    with open(tmp_path / "test.typ", mode="wt") as f:
        f.write(heading.render())

    typst.compile(tmp_path / "test.typ")
