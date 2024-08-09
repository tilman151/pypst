import pytest
import typst

from pypst.figure import Figure


class DummyBody:
    def render(self):
        return "#text(fill: red)[Hello, world!]"


def test_dummy_figure():
    figure = Figure(DummyBody())
    assert figure.render() == "#figure(\ntext(fill: red)[Hello, world!]\n)"


def test_figure_with_placement():
    figure = Figure(DummyBody(), placement="top")
    assert figure.render() == (
        "#figure(\ntext(fill: red)[Hello, world!],\nplacement: top\n)"
    )


def test_figure_with_caption():
    figure = Figure(DummyBody(), caption='"This is a caption"')
    assert figure.render() == (
        '#figure(\ntext(fill: red)[Hello, world!],\ncaption: "This is a caption"\n)'
    )


def test_figure_with_kind():
    figure = Figure(DummyBody(), kind="table")
    assert figure.render() == (
        "#figure(\ntext(fill: red)[Hello, world!],\nkind: table\n)"
    )


def test_figure_with_supplement():
    figure = Figure(DummyBody(), supplement='"Table"')
    assert figure.render() == (
        '#figure(\ntext(fill: red)[Hello, world!],\nsupplement: "Table"\n)'
    )


def test_figure_with_numbering():
    figure = Figure(DummyBody(), numbering='"1"')
    assert figure.render() == (
        '#figure(\ntext(fill: red)[Hello, world!],\nnumbering: "1"\n)'
    )


def test_figure_with_gap():
    figure = Figure(DummyBody(), gap="10pt")
    assert figure.render() == (
        "#figure(\ntext(fill: red)[Hello, world!],\ngap: 10pt\n)"
    )


def test_figure_with_outlined():
    figure = Figure(DummyBody(), outlined=True)
    assert figure.render() == (
        "#figure(\ntext(fill: red)[Hello, world!],\noutlined: true\n)"
    )


@pytest.mark.integration
def test_render(tmp_path):
    figure = Figure(
        DummyBody(),
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
