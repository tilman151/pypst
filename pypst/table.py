import itertools
from typing import Any, Optional, Union, Literal

import pandas as pd

__all__ = ["Table", "Cell"]


class Table:
    header_data: list[list["Cell"]]
    index_data: list[list["Cell"]]
    row_data: list[list["Cell"]]
    columns: Optional[int]
    rows: Optional[int]

    def __init__(self) -> None:
        self.header_data = []
        self.index_data = []
        self.row_data = []

        self.columns = None
        self.rows = None

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> "Table":
        table = cls()
        table.header_data = _parse_index(df.columns, direction="cols")
        table.index_data = _parse_index(df.index, direction="rows")
        for _, *row in df.itertuples():
            table.row_data.append([Cell(value) for value in row])
        table.columns = len(df.columns) + df.index.nlevels

        return table

    def __str__(self) -> str:
        return self.render()

    def __repr__(self) -> str:
        return f"Table(headers={self.header_data}, index={self.index_data}, rows={self.row_data})"

    def render(self) -> str:
        headers = itertools.chain(*self.header_data)
        index_placeholder = Cell(
            rowspan=len(self.header_data), colspan=len(self.index_data)
        )
        table = (
            "#table(\n"
            + self._render_args()
            + "table.header"
            + index_placeholder.render()
            + "".join(header.render() for header in headers)
            + ",\n"
            + self._render_rows()
            + ")"
        )

        return table

    def _render_args(self) -> str:
        args = []
        if self.columns is not None:
            args.append(f"columns: {self.columns}")
        if self.rows is not None:
            args.append(f"rows: {self.rows}")
        rendered_args = ",\n".join(args) + ",\n"

        return rendered_args

    def _render_rows(self) -> str:
        table = ""
        rows_to_skip = [0] * len(self.index_data)
        index_positions = [0] * len(self.index_data)
        for row in self.row_data:
            for level in range(len(self.index_data)):
                if rows_to_skip[level] == 0:
                    index_cell = self.index_data[level][index_positions[level]]
                    table += index_cell.render() + ", "
                    index_positions[level] += 1
                    rows_to_skip[level] = index_cell.rowspan
                rows_to_skip[level] -= 1
            table += ", ".join(cell.render() for cell in row) + ",\n"

        return table


class Cell:
    def __init__(
        self, value: Optional[Any] = None, rowspan: int = 1, colspan: int = 1
    ) -> None:
        self.value = value
        self.rowspan = rowspan
        self.colspan = colspan

    def __str__(self) -> str:
        return self.render()

    def __repr__(self) -> str:
        return (
            f"Cell(value={self.value}, rowspan={self.rowspan}, colspan={self.colspan})"
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Cell):
            return False

        return (
            self.value == other.value
            and self.rowspan == other.rowspan
            and self.colspan == other.colspan
        )

    def render(self) -> str:
        cell = "[]" if self.value is None else f"[{self.value}]"
        if self.rowspan > 1 or self.colspan > 1:
            args = []
            if self.rowspan > 1:
                args.append(f"rowspan: {self.rowspan}")
            if self.colspan > 1:
                args.append(f"colspan: {self.colspan}")
            cell = f"[#table.cell({', '.join(args)}){cell}]"

        return cell


def _parse_index(
    index: Union[pd.Index, pd.MultiIndex], direction: Literal["rows", "cols"]
) -> list[list["Cell"]]:
    headers: list[list[Cell]]
    if index.empty:
        headers = [[]]
    elif isinstance(index, pd.MultiIndex):
        headers = _parse_multi_index(index, direction)
    else:
        headers = [[Cell(header, colspan=1) for header in index]]

    return headers


def _parse_multi_index(
    index: pd.MultiIndex, direction: Literal["rows", "cols"]
) -> list[list["Cell"]]:
    assert not index.empty
    headers = []
    for level in range(index.nlevels):
        headers.append(_parse_level(index, level, direction))

    return headers


def _parse_level(
    index: pd.MultiIndex, level: int, direction: Literal["rows", "cols"]
) -> list["Cell"]:
    span_arg = _get_span_arg(direction)
    level_codes = index.codes[level]
    headers = []
    span = 0
    prev_code = level_codes[0]
    for code in level_codes:
        if code == prev_code:
            span += 1
        else:
            headers.append(Cell(index.levels[level][prev_code]))
            setattr(headers[-1], span_arg, span)
            prev_code = code
            span = 1
    headers.append(Cell(index.levels[level][-1]))
    setattr(headers[-1], span_arg, span)

    return headers


def _get_span_arg(direction: Literal["rows", "cols"]) -> str:
    if direction == "rows":
        span_arg = "rowspan"
    elif direction == "cols":
        span_arg = "colspan"
    else:
        raise ValueError(f"Invalid direction: {direction}")

    return span_arg
