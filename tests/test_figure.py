import pytest
import typst

from pypst.figure import Figure
from tests.conftest import DummyBody


def test_dummy_figure(dummy_body):
    figure = Figure(DummyBody())
    assert figure.render() == "#figure(text(fill: red)[Hello, world!])"


def test_figure_with_placement(dummy_body):
    figure = Figure(dummy_body, placement="top")
    rendered = figure.render()
    assert rendered == "#figure(text(fill: red)[Hello, world!], placement: top)"


def test_figure_with_caption(dummy_body):
    figure = Figure(dummy_body, caption='"This is a caption"')
    rendered = figure.render()
    assert rendered == (
        '#figure(text(fill: red)[Hello, world!], caption: "This is a caption")'
    )


def test_figure_with_kind(dummy_body):
    figure = Figure(dummy_body, kind="table")
    rendered = figure.render()
    assert rendered == "#figure(text(fill: red)[Hello, world!], kind: table)"


def test_figure_with_supplement(dummy_body):
    figure = Figure(dummy_body, supplement='"Table"')
    rendered = figure.render()
    assert rendered == ('#figure(text(fill: red)[Hello, world!], supplement: "Table")')


def test_figure_with_numbering(dummy_body):
    figure = Figure(dummy_body, numbering='"1"')
    rendered = figure.render()
    assert rendered == '#figure(text(fill: red)[Hello, world!], numbering: "1")'


def test_figure_with_gap(dummy_body):
    figure = Figure(dummy_body, gap="10pt")
    rendered = figure.render()
    assert rendered == "#figure(text(fill: red)[Hello, world!], gap: 10pt)"


def test_figure_with_outlined(dummy_body):
    figure = Figure(dummy_body, outlined=True)
    rendered = figure.render()
    assert rendered == "#figure(text(fill: red)[Hello, world!], outlined: true)"


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
