import itertools

import numpy as np
import pandas as pd
import pytest

from pypst import Table

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
