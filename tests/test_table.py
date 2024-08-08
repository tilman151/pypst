from copy import deepcopy

import pandas as pd
import pytest
import typst

from pypst import Table, Cell


@pytest.fixture
def df():
    table = pd.DataFrame(
        {
            "A": [1, 2, 3],
            "B": [4, 5, 6],
            "C": [7, 8, 9],
        }
    )
    table = Table.from_dataframe(table)

    return table


@pytest.fixture
def multi_frame():
    return pd.DataFrame(
        {
            ("A", "X"): [1, 2, 3],
            ("A", "Y"): [4, 5, 6],
            ("B", "X"): [7, 8, 9],
            ("B", "Y"): [10, 11, 12],
        }
    )


@pytest.fixture
def df_multi_header(multi_frame):
    table = Table.from_dataframe(multi_frame)

    return table


@pytest.fixture
def df_multi_index(multi_frame):
    table = Table.from_dataframe(multi_frame.T)

    return table


@pytest.fixture
def df_custom_col(df):
    table = deepcopy(df)
    table.columns = ["10%", "20%", "30%", "40%"]

    return table


@pytest.fixture
def df_custom_row(df):
    table = deepcopy(df)
    table.rows = ["10%", "20%", "30%", "40%"]

    return table


def test_from_dataframe_simple_headers(df):
    assert df.header_data == [[Cell("A"), Cell("B"), Cell("C")]]


def test_from_dataframe_multi_headers(df_multi_header):
    assert df_multi_header.header_data == [
        [Cell("A", colspan=2), Cell("B", colspan=2)],
        [Cell("X"), Cell("Y"), Cell("X"), Cell("Y")],
    ]


def test_render_simple_table(df):
    assert df.render() == (
        "#table(\ncolumns: 4,\ntable.header[][A][B][C],"
        "\n[0], [1], [4], [7],"
        "\n[1], [2], [5], [8],"
        "\n[2], [3], [6], [9],\n)"
    )


def test_render_multi_header(df_multi_header):
    assert df_multi_header.render() == (
        "#table(\ncolumns: 5,\n"
        "table.header[#table.cell(rowspan: 2)[]]"
        "[#table.cell(colspan: 2)[A]][#table.cell(colspan: 2)[B]]"
        "[X][Y][X][Y],\n"
        "[0], [1], [4], [7], [10],\n"
        "[1], [2], [5], [8], [11],\n"
        "[2], [3], [6], [9], [12],\n)"
    )


def test_render_multi_index(df_multi_index):
    assert df_multi_index.render() == (
        "#table(\n"
        "columns: 5,\n"
        "table.header[#table.cell(colspan: 2)[]][0][1][2],\n"
        "[#table.cell(rowspan: 2)[A]], [X], [1], [2], [3],\n"
        "[Y], [4], [5], [6],\n"
        "[#table.cell(rowspan: 2)[B]], [X], [7], [8], [9],\n"
        "[Y], [10], [11], [12],\n"
        ")"
    )


def test_render_custom_col(df_custom_col):
    assert df_custom_col.render() == (
        "#table(\ncolumns: (10%, 20%, 30%, 40%),\ntable.header[][A][B][C],"
        "\n[0], [1], [4], [7],"
        "\n[1], [2], [5], [8],"
        "\n[2], [3], [6], [9],\n)"
    )


def test_render_custom_row(df_custom_row):
    assert df_custom_row.render() == (
        "#table(\ncolumns: 4,\nrows: (10%, 20%, 30%, 40%),\ntable.header[][A][B][C],"
        "\n[0], [1], [4], [7],"
        "\n[1], [2], [5], [8],"
        "\n[2], [3], [6], [9],\n)"
    )


@pytest.mark.parametrize(
    "table", ["df", "df_multi_index", "df_custom_col", "df_custom_row"]
)
def test_compilation(table, tmp_path, request):
    table = request.getfixturevalue(table)
    with open(tmp_path / "table.typ", mode="wt") as f:
        f.write(table.render())

    typst.compile(tmp_path / "table.typ")


@pytest.mark.skip("Visual test")
def test_compilation_visual(
    df, df_multi_header, df_multi_index, df_custom_col, df_custom_row
):
    table = (
        df.render()
        + "\n"
        + df_multi_header.render()
        + "\n"
        + df_multi_index.render()
        + "\n"
        + df_custom_col.render()
        + "\n"
        + df_custom_row.render()
    )
    with open("table.typ", mode="wt") as f:
        f.write(table)

    typst.compile("table.typ", "table.pdf")


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
