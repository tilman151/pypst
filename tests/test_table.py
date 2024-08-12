import pytest
import typst
from frozenlist import FrozenList

from pypst import Cell
from pypst.table import TableLine
from tests.conftest import generate_all_combinations


def test_from_dataframe_simple_headers(df):
    assert df.header_data == [[Cell("A"), Cell("B"), Cell("C")]]


def test_from_dataframe_multi_headers(df_multi_header):
    assert df_multi_header.header_data == [
        [Cell("A", colspan=2), Cell("B", colspan=2)],
        [Cell("X"), Cell("Y"), Cell("X"), Cell("Y")],
    ]


def test_render_simple_table(df):
    rendered = df.render().replace("\n  ", "\n")
    assert rendered == (
        "#table(\ncolumns: 4,\ntable.header[][A][B][C],"
        "\n[0], [1], [4], [7],"
        "\n[1], [2], [5], [8],"
        "\n[2], [3], [6], [9]\n)"
    )


def test_render_multi_header(df_multi_header):
    rendered = df_multi_header.render().replace("\n  ", "\n")
    assert rendered == (
        "#table(\ncolumns: 5,\n"
        "table.header[#table.cell(rowspan: 2)[]]"
        "[#table.cell(colspan: 2)[A]][#table.cell(colspan: 2)[B]]"
        "[X][Y][X][Y],\n"
        "[0], [1], [4], [7], [10],\n"
        "[1], [2], [5], [8], [11],\n"
        "[2], [3], [6], [9], [12]\n)"
    )


def test_render_multi_index(df_multi_index):
    rendered = df_multi_index.render().replace("\n  ", "\n")
    assert rendered == (
        "#table(\n"
        "columns: 5,\n"
        "table.header[#table.cell(colspan: 2)[]][0][1][2],\n"
        "[#table.cell(rowspan: 2)[A]], [X], [1], [2], [3],\n"
        "[Y], [4], [5], [6],\n"
        "[#table.cell(rowspan: 2)[B]], [X], [7], [8], [9],\n"
        "[Y], [10], [11], [12]\n"
        ")"
    )


def test_render_custom_col(df):
    df.columns = ["10%", "20%", "30%", "40%"]
    rendered = df.render().replace("\n  ", "\n")
    assert rendered == (
        "#table(\ncolumns: (10%, 20%, 30%, 40%),\ntable.header[][A][B][C],"
        "\n[0], [1], [4], [7],"
        "\n[1], [2], [5], [8],"
        "\n[2], [3], [6], [9]\n)"
    )


def test_render_custom_row(df):
    df.rows = ["10%", "20%", "30%", "40%"]
    rendered = df.render().replace("\n  ", "\n")
    assert rendered == (
        "#table(\ncolumns: 4,\nrows: (10%, 20%, 30%, 40%),\ntable.header[][A][B][C],"
        "\n[0], [1], [4], [7],"
        "\n[1], [2], [5], [8],"
        "\n[2], [3], [6], [9]\n)"
    )


@pytest.mark.parametrize(
    "stroke, rendered_stroke",
    [
        ("none",) * 2,
        ("3pt",) * 2,
        ("(x, _) => if x > 1 { 1pt } else { 0pt }",) * 2,
        (["3pt", "2pt", "1pt"], "(3pt, 2pt, 1pt)"),
        ({"top": "1pt", "bottom": "2pt"}, "(top: 1pt, bottom: 2pt)"),
    ],
)
def test_render_custom_stroke(df, stroke, rendered_stroke):
    df.stroke = stroke
    rendered = df.render().replace("\n  ", "\n")
    assert rendered == (
        f"#table(\ncolumns: 4,\nstroke: {rendered_stroke},\ntable.header[][A][B][C],"
        "\n[0], [1], [4], [7],"
        "\n[1], [2], [5], [8],"
        "\n[2], [3], [6], [9]\n)"
    )


@pytest.mark.parametrize(
    "align, rendered_align",
    [
        ("center",) * 2,
        ("(x, _) => if x > 1 { left } else { right }",) * 2,
        (["left", "center", "right"], "(left, center, right)"),
    ],
)
def test_render_custom_align(df, align, rendered_align):
    df.align = align
    rendered = df.render().replace("\n  ", "\n")
    assert rendered == (
        f"#table(\ncolumns: 4,\nalign: {rendered_align},\ntable.header[][A][B][C],"
        "\n[0], [1], [4], [7],"
        "\n[1], [2], [5], [8],"
        "\n[2], [3], [6], [9]\n)"
    )


@pytest.mark.parametrize(
    "fill, rendered_fill",
    [
        ("blue",) * 2,
        ("(x, _) => if x > 1 { blue } else { red }",) * 2,
        (["blue", "red", "green"], "(blue, red, green)"),
    ],
)
def test_render_custom_fill(df, fill, rendered_fill):
    df.fill = fill
    rendered = df.render().replace("\n  ", "\n")
    assert rendered == (
        f"#table(\ncolumns: 4,\nfill: {rendered_fill},\ntable.header[][A][B][C],"
        "\n[0], [1], [4], [7],"
        "\n[1], [2], [5], [8],"
        "\n[2], [3], [6], [9]\n)"
    )


@pytest.mark.parametrize("gutter_attribute", ["gutter", "column_gutter", "row_gutter"])
@pytest.mark.parametrize(
    "gutter, rendered_gutter",
    [
        (1,) * 2,
        ("5%",) * 2,
        (["1%", "2%", "3%"], "(1%, 2%, 3%)"),
    ],
)
def test_render_custom_gutter(df, gutter_attribute, gutter, rendered_gutter):
    setattr(df, gutter_attribute, gutter)
    rendered = df.render().replace("\n  ", "\n")
    assert rendered == (
        f"#table(\ncolumns: 4,\n{gutter_attribute.replace('_', '-')}: {rendered_gutter},"
        f"\ntable.header[][A][B][C],"
        "\n[0], [1], [4], [7],"
        "\n[1], [2], [5], [8],"
        "\n[2], [3], [6], [9]\n)"
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
    rendered = df.render().replace("\n  ", "\n")
    assert rendered == (
        f"#table(\ncolumns: 4,\n{rendered_lines},\ntable.header[][A][B][C],"
        "\n[0], [1], [4], [7],"
        "\n[1], [2], [5], [8],"
        "\n[2], [3], [6], [9]\n)"
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


@pytest.mark.integration
def test_compilation(all_combinations, tmp_path):
    with open(tmp_path / "table.typ", mode="wt") as f:
        f.write(all_combinations.render())

    typst.compile(tmp_path / "table.typ")


@pytest.mark.visual
def test_compilation_visual():
    _, all_combinations = generate_all_combinations()
    table = "\n#pagebreak()\n".join([t.render() for t in all_combinations])
    with open("table.typ", mode="wt") as f:
        f.write(table)

    typst.compile("table.typ", "table.pdf")


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
