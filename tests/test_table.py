import itertools

import numpy as np
import pandas as pd

import pytest
import typst
from frozenlist import FrozenList

from pypst import Table, Cell
from pypst.table import TableLine

DATA_FRAME = pd.DataFrame(
    {
        "A": [1, 2, 3],
        "B": [4, 5, 6],
        "C": [7, 8, 9],
    }
)
MULTI_FRAME = pd.DataFrame(
    {
        ("A", "X"): [1, 2, 3],
        ("A", "Y"): [4, 5, 6],
        ("B", "X"): [7, 8, 9],
        ("B", "Y"): [10, 11, 12],
    }
)


@pytest.fixture
def df():
    return Table.from_dataframe(DATA_FRAME)


@pytest.fixture
def df_multi_header():
    table = Table.from_dataframe(MULTI_FRAME)

    return table


@pytest.fixture
def df_multi_index():
    table = Table.from_dataframe(MULTI_FRAME.T)

    return table


def pytest_generate_tests(metafunc):
    if "all_combinations" in metafunc.fixturenames:
        ids, all_combinations = generate_all_combinations()
        metafunc.parametrize("all_combinations", all_combinations, ids=ids)


def generate_all_combinations():
    all_combinations = []
    ids = []
    for df_name, df in {
        "simple": DATA_FRAME,
        "multi_header": MULTI_FRAME,
        "multi_index": MULTI_FRAME.T,
    }.items():
        num_cols = len(df.columns) + df.index.nlevels
        columns = [
            num_cols,
            [f"{p}%" for p in np.linspace(10, 50, num_cols)],
            [f"{c}cm" for c in range(1, num_cols + 1)],
        ]
        num_rows = len(df) + df.columns.nlevels
        rows = [
            num_rows,
            [f"{p}%" for p in np.linspace(10, 50, num_rows)],
            [f"{c}cm" for c in range(1, num_rows + 1)],
        ]
        strokes = [
            None,
            "3pt",
            "(x, _) => if calc.odd(x) { 1pt } else { 0pt }",
            ["3pt", "2pt", "1pt"],
            {"top": "1pt", "bottom": "2pt"},
        ]
        line_options = [
            [],
            [("h", (0, 1, 3, "red"))],
            [("v", (0, 1, 3, "blue"))],
            [("h", (0, 1, 3, "red")), ("v", (0, 1, 3, "blue"))],
        ]
        for col, row, stroke, lines in itertools.product(
            columns, rows, strokes, line_options
        ):
            table = Table.from_dataframe(df)
            table.columns = col
            table.rows = row
            table.stroke = stroke
            for orientation, args in lines:
                if orientation == "h":
                    table.add_hline(*args)
                else:
                    table.add_vline(*args)
            all_combinations.append(table)
            ids.append(
                f"type: {df_name}, columns: {col}, rows: {row}, stroke: {stroke}"
            )

    return ids, all_combinations


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


def test_render_custom_col(df):
    df.columns = ["10%", "20%", "30%", "40%"]
    assert df.render() == (
        "#table(\ncolumns: (10%, 20%, 30%, 40%),\ntable.header[][A][B][C],"
        "\n[0], [1], [4], [7],"
        "\n[1], [2], [5], [8],"
        "\n[2], [3], [6], [9],\n)"
    )


def test_render_custom_row(df):
    df.rows = ["10%", "20%", "30%", "40%"]
    assert df.render() == (
        "#table(\ncolumns: 4,\nrows: (10%, 20%, 30%, 40%),\ntable.header[][A][B][C],"
        "\n[0], [1], [4], [7],"
        "\n[1], [2], [5], [8],"
        "\n[2], [3], [6], [9],\n)"
    )


@pytest.mark.parametrize(
    "stroke, rendered_stroke",
    [
        (None, "none"),
        ("3pt",) * 2,
        ("(x, _) => if x > 1 { 1pt } else { 0pt }",) * 2,
        (["3pt", "2pt", "1pt"], "(3pt, 2pt, 1pt)"),
        ({"top": "1pt", "bottom": "2pt"}, "(top: 1pt, bottom: 2pt)"),
    ],
)
def test_render_custom_stroke(df, stroke, rendered_stroke):
    df.stroke = stroke
    assert df.render() == (
        f"#table(\ncolumns: 4,\nstroke: {rendered_stroke},\ntable.header[][A][B][C],"
        "\n[0], [1], [4], [7],"
        "\n[1], [2], [5], [8],"
        "\n[2], [3], [6], [9],\n)"
    )


@pytest.mark.parametrize(
    "lines, rendered_lines",
    [
        ([("h", 1)], "table.hline(y: 1)"),
        ([("h", 1), ("v", 2)], "table.hline(y: 1),\ntable.vline(x: 2)"),
    ],
)
def test_render_lines(df, lines, rendered_lines):
    for orientation, line in lines:
        if orientation == "h":
            df.add_hline(line)
        else:
            df.add_vline(line)
    assert df.render() == (
        f"#table(\ncolumns: 4,\n{rendered_lines},\ntable.header[][A][B][C],"
        "\n[0], [1], [4], [7],"
        "\n[1], [2], [5], [8],"
        "\n[2], [3], [6], [9],\n)"
    )


@pytest.mark.parametrize("table", ["df", "df_multi_index"])
def test_attributes_are_frozen(table, tmp_path, request):
    table = request.getfixturevalue(table)

    def _check_all_frozen(obj):
        assert isinstance(obj, FrozenList)
        assert obj.frozen
        for element in obj:
            assert isinstance(element, FrozenList)
            assert element.frozen

    _check_all_frozen(table.header_data)
    _check_all_frozen(table.index_data)
    _check_all_frozen(table.row_data)


def test_compilation(all_combinations, tmp_path):
    with open(tmp_path / "table.typ", mode="wt") as f:
        f.write(all_combinations.render())

    typst.compile(tmp_path / "table.typ")


@pytest.mark.skip("Visual test")
def test_compilation_visual():
    _, all_combinations = generate_all_combinations()
    table = "\n#pagebreak()\n".join([t.render() for t in all_combinations])
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


@pytest.mark.parametrize(
    "orientation, prefix",
    [("horizontal", "table.hline(y: "), ("vertical", "table.vline(x: ")],
)
class TestTableLine:
    @pytest.mark.parametrize("pos", [1, 2, 3])
    def test_pos(self, orientation, prefix, pos):
        line = TableLine(pos, orientation=orientation)
        assert line.render() == prefix + f"{pos})"

    @pytest.mark.parametrize("start", [1, 2, 3])
    def test_start(self, orientation, prefix, start):
        line = TableLine(1, start=start, orientation=orientation)
        assert line.render() == prefix + f"1, start: {start})"

    @pytest.mark.parametrize("end", [1, 2, 3])
    def test_end(self, orientation, prefix, end):
        line = TableLine(1, end=end, orientation=orientation)
        assert line.render() == prefix + f"1, end: {end})"

    @pytest.mark.parametrize(
        "stroke, rendered_stroke",
        [
            ("3pt",) * 2,
            ({"paint": "blue", "thickness": "3pt"}, "(paint: blue, thickness: 3pt)"),
        ],
    )
    def test_stroke(self, orientation, prefix, stroke, rendered_stroke):
        line = TableLine(1, stroke=stroke, orientation=orientation)
        assert line.render() == prefix + f"1, stroke: {rendered_stroke})"

    @pytest.mark.parametrize("position", ["start", "end"])
    def test_position(self, orientation, prefix, position):
        line = TableLine(1, position=position, orientation=orientation)
        assert line.render() == prefix + f"1, position: {position})"
