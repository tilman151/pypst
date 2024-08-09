import pytest
import typst

from pypst.figure import Figure
from tests.conftest import DummyBody


def test_dummy_figure(dummy_body):
    figure = Figure(DummyBody())
    assert figure.render() == "#figure(\ntext(fill: red)[Hello, world!]\n)"


def test_figure_with_placement(dummy_body):
    figure = Figure(dummy_body, placement="top")
    assert figure.render() == (
        "#figure(\ntext(fill: red)[Hello, world!],\nplacement: top\n)"
    )


def test_figure_with_caption(dummy_body):
    figure = Figure(dummy_body, caption='"This is a caption"')
    assert figure.render() == (
        '#figure(\ntext(fill: red)[Hello, world!],\ncaption: "This is a caption"\n)'
    )


def test_figure_with_kind(dummy_body):
    figure = Figure(dummy_body, kind="table")
    assert figure.render() == (
        "#figure(\ntext(fill: red)[Hello, world!],\nkind: table\n)"
    )


def test_figure_with_supplement(dummy_body):
    figure = Figure(dummy_body, supplement='"Table"')
    assert figure.render() == (
        '#figure(\ntext(fill: red)[Hello, world!],\nsupplement: "Table"\n)'
    )


def test_figure_with_numbering(dummy_body):
    figure = Figure(dummy_body, numbering='"1"')
    assert figure.render() == (
        '#figure(\ntext(fill: red)[Hello, world!],\nnumbering: "1"\n)'
    )


def test_figure_with_gap(dummy_body):
    figure = Figure(dummy_body, gap="10pt")
    assert figure.render() == (
        "#figure(\ntext(fill: red)[Hello, world!],\ngap: 10pt\n)"
    )


def test_figure_with_outlined(dummy_body):
    figure = Figure(dummy_body, outlined=True)
    assert figure.render() == (
        "#figure(\ntext(fill: red)[Hello, world!],\noutlined: true\n)"
    )


@pytest.mark.integration
def test_render(dummy_body, tmp_path):
    figure = Figure(
        dummy_body,
        placement="top",
        caption='"This is a caption"',
        kind="table",
        supplement='"Table"',
        numbering='"1"',
        gap="10pt",
        outlined=True,
    )
    with open(tmp_path / "figure.typ", mode="wt") as f:
        f.write(figure.render())

    typst.compile(tmp_path / "figure.typ")
