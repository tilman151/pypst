import pandas as pd
import pytest
import typst

from pypst import Table, Cell


@pytest.fixture
def df():
    return pd.DataFrame(
        {
            "A": [1, 2, 3],
            "B": [4, 5, 6],
            "C": [7, 8, 9],
        }
    )


@pytest.fixture
def df_multi_index():
    return pd.DataFrame(
        {
            ("A", "X"): [1, 2, 3],
            ("A", "Y"): [4, 5, 6],
            ("B", "X"): [7, 8, 9],
            ("B", "Y"): [10, 11, 12],
        }
    )


def test_from_dataframe_simple_headers(df):
    table = Table.from_dataframe(df)
    assert table.headers == [Cell("A"), Cell("B"), Cell("C")]


def test_from_dataframe_multi_headers(df_multi_index):
    table = Table.from_dataframe(df_multi_index)
    assert table.headers == [
        Cell("A", colspan=2),
        Cell("B", colspan=2),
        Cell("X"),
        Cell("Y"),
        Cell("X"),
        Cell("Y"),
    ]


def test_render_simple_table(df):
    table = Table.from_dataframe(df)
    assert table.render() == "#table(\ncolumns: 3,\ntable.header[A][B][C]\n)"


def test_render_multi_table(df_multi_index):
    table = Table.from_dataframe(df_multi_index)
    assert (
        table.render() == "#table(\ncolumns: 4,\n"
        "table.header[#table.cell(colspan: 2)[A]]"
        "[#table.cell(colspan: 2)[B]]"
        "[X][Y][X][Y]\n)"
    )


@pytest.mark.parametrize("table", ["df", "df_multi_index"])
def test_compilation(table, tmp_path, request):
    table = request.getfixturevalue(table)
    with open(tmp_path / "table.typ", mode="wt") as f:
        f.write(Table.from_dataframe(table).render())

    typst.compile(tmp_path / "table.typ")


class TestCell:
    def test_empty_cell(self):
        cell = Cell()
        assert cell.render() == "[]"

    def test_cell_with_value(self):
        cell = Cell("value")
        assert cell.render() == "[value]"

    def test_cell_with_rowspan(self):
        cell = Cell("value", rowspan=2)
        assert cell.render() == "[#table.cell(rowspan: 2)[value]]"

    def test_cell_with_colspan(self):
        cell = Cell("value", colspan=2)
        assert cell.render() == "[#table.cell(colspan: 2)[value]]"

    def test_cell_with_rowspan_and_colspan(self):
        cell = Cell("value", rowspan=3, colspan=2)
        assert cell.render() == "[#table.cell(rowspan: 3, colspan: 2)[value]]"
