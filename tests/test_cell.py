import pytest

from pypst import Cell


def test_empty_cell():
    cell = Cell()
    assert cell.render() == "[]"


def test_cell_with_value():
    cell = Cell("value")
    assert cell.render() == "[value]"


def test_cell_with_rowspan():
    cell = Cell("value", rowspan=2)
    assert cell.render() == "[#table.cell(rowspan: 2)[value]]"


def test_cell_with_colspan():
    cell = Cell("value", colspan=2)
    assert cell.render() == "[#table.cell(colspan: 2)[value]]"


def test_cell_with_rowspan_and_colspan():
    cell = Cell("value", rowspan=3, colspan=2)
    assert cell.render() == "[#table.cell(rowspan: 3, colspan: 2)[value]]"


def test_cell_with_fill():
    cell = Cell("value", fill="red")
    assert cell.render() == "[#table.cell(fill: red)[value]]"


@pytest.mark.parametrize(
    "stroke, rendered_stroke",
    [("3pt",) * 2, ({"top": "1pt", "bottom": "2pt"}, "(top: 1pt, bottom: 2pt)")],
)
def test_cell_with_stroke(stroke, rendered_stroke):
    cell = Cell("value", stroke=stroke)
    assert cell.render() == f"[#table.cell(stroke: {rendered_stroke})[value]]"
