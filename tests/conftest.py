import itertools

import numpy as np
import pandas as pd
import pytest

from pypst import Table

IMAGE_DATA = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\n\x00\x00\x00\n\x08"
    b"\x02\x00\x00\x00\x02PX\xea\x00\x00\x01~iCCPICC profile\x00\x00(\x91}"
    b"\x919H\x03Q\x14E\xcfL\x94\x04\x89\xa40\x85\x88\xc5\x14.M\xd2\xa8\x88e"
    b"\x8cB\x10\x14B\x8c\x90\xa8\x85\xb3\x98\x052c\x98\x99`\x93R\xb0\x15,\\\x1a"
    b"\xb7\xc2\xc6Z[\x0b[A\x10\\@\xac-\xac\x14mDF~\x12H\x10\xe3k\xfe\xe1\xfew"
    b"\x1f\xff\xdd\x0f\xf2aI7\x9d\x8e\x18\x98\x96k\xa7\x12q%\x93]T\xfc/\x04\x08"
    b"\xe1g\x98\x88\xaa;\xe5\xc9dr\x96\xb6\xf5y\x87$\xce\xdb\xa8\x98\xd5\xbe\xef"
    b"\xcf\xea6V\x1d\x1d$\x05\x88\xe9e\xdb\x05i\x05\x18_w\xcb\x82w\x81\xb0^P\r"
    b"\x90\xce\x80\x88\x9d\xc9.\x82\xf4 t\xad\xce\xaf\x82\xf35\x96\xc5\xcc\xb0"
    b"\x9dNM\x81\x1c\x06\x94|\x0bk-\xac\x17l\x13\xe41`\xc00-\x03\xe4L\x9d\r\xc1U"
    b"\xc1f\xa9\xa27\xde)6\x0c\xaeZ\x0b\xf3B\x07\xfaI0\xc3\x1cI\x144*\x14)\xe1"
    b"\x12\xa5\x88\x85\x82C\x8a\x04\xf16\xfe\xbe\x9a?I\x05\x8d\x12Et\x14\xa6Y\xc3D"
    b"\xad\xf9\x11\x7f\xf0;['7:R\x9f\x14\x8cC\xe7\xb3\xe7\xbd\x0f\x82\x7f\x1b\xbe"
    b"\xb7<\xef\xeb\xc8\xf3\xbe\x8f\xc1\xf7\x04\x97V\xd3\xbfv\x08\x13\x1f\xe0\xdbjj"
    b"\x03\x07\x10\xda\x80\xf3\xab\xa6\xa6\xed\xc0\xc5&\xf4>\x96U[\xadI>@\xce\xe5"
    b"\xe0\xed\x14\xba\xb3\xd0s\x03]K\xf5\xdc\x1a\xf7\x9c\xdcC\xba\n\xb3\xd7\xb0\xb7"
    b'\x0fCy\x08-\xb7\xd9;\xd0\x9a\xdb\xbf=\x8d\xfc~\x00\xb7\xdcr\xc2g"\xfd\x7f\x00'
    b"\x00\x00\tpHYs\x00\x00.#\x00\x00.#\x01x\xa5?v\x00\x00\x00\x07tIME\x07\xe8\x08"
    b"\x0f\x07(.\xda\x14\xdd8\x00\x00\x00\x19tEXtComment\x00Created with GIMPW\x81"
    b"\x0e\x17\x00\x00\x00\rIDAT\x18\xd3c`\x18\x05\xa4\x03\x00\x016\x00\x01\x1a\xd5"
    b"\x8d\x17\x00\x00\x00\x00IEND\xaeB`\x82"
)

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


@pytest.fixture
def styled_table(request):
    return create_table(*request.param)


def pytest_generate_tests(metafunc):
    if "styled_table" in metafunc.fixturenames:
        ids, combinations = sample_combinations(1000, seed=42)
        metafunc.parametrize("styled_table", combinations, ids=ids, indirect=True)


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
        aligns = [
            None,
            "center",
            "(x, _) => if calc.odd(x) { left } else { right }",
            ["left", "center", "right"],
        ]
        fills = [
            None,
            "red",
            "(x, _) => if calc.odd(x) { green } else { yellow }",
            ["red", "blue", "green"],
        ]
        gutters = [
            None,
            1,
            "1%",
            ["1%", "2%", "3%"],
        ]
        line_options = [
            [],
            [("h", (0, 1, 3, "red"))],
            [("v", (0, 1, 3, "blue"))],
            [("h", (0, 1, 3, "red")), ("v", (0, 1, 3, "blue"))],
        ]
        for (
            col,
            row,
            stroke,
            align,
            fill,
            gutter,
            column_gutter,
            row_gutter,
            lines,
        ) in itertools.product(
            columns,
            rows,
            strokes,
            aligns,
            fills,
            gutters,
            gutters,
            gutters,
            line_options,
        ):
            all_combinations.append(
                (
                    df,
                    col,
                    row,
                    stroke,
                    align,
                    fill,
                    gutter,
                    column_gutter,
                    row_gutter,
                    lines,
                )
            )
            ids.append(
                (
                    f"type: {df_name}, columns: {col}, rows: {row}, "
                    f"stroke: {stroke}, align: {align}, fill: {fill}, "
                    f"gutter: {gutter}, column-gutter: {column_gutter}, "
                    f"row-gutter: {row_gutter}, lines: {len(lines)}"
                )
            )

    return ids, all_combinations


def sample_combinations(num_samples, seed=None):
    all_ids, all_combinations = generate_all_combinations()
    sample_idx = np.random.default_rng(seed).choice(
        range(len(all_combinations)), num_samples, replace=False
    )
    return [all_ids[i] for i in sample_idx], [all_combinations[i] for i in sample_idx]


def create_table(
    df, col, row, stroke, align, fill, gutter, column_gutter, row_gutter, lines
):
    table = Table.from_dataframe(df)
    table.columns = col
    table.rows = row
    table.stroke = stroke
    table.align = align
    table.fill = fill
    table.gutter = gutter
    table.column_gutter = column_gutter
    table.row_gutter = row_gutter
    for orientation, args in lines:
        if orientation == "h":
            table.add_hline(*args)
        else:
            table.add_vline(*args)

    return table


class DummyBody:
    def render(self):
        return "#text(fill: red)[Hello, world!]"


@pytest.fixture
def dummy_body():
    return DummyBody()


@pytest.fixture
def image_on_disk(tmp_path):
    image_path = tmp_path / "image.png"
    with open(image_path, mode="wb") as f:
        f.write(IMAGE_DATA)

    return image_path
