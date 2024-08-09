import itertools
from dataclasses import dataclass
from typing import Optional, Union, Literal

import pandas as pd
from frozendict import frozendict

from frozenlist import FrozenList

from pypst.cell import Cell
from pypst.utils import render_arg, render_mapping


@dataclass
class Table:
    header_data: FrozenList[FrozenList["Cell"]] = FrozenList(FrozenList([]))
    index_data: FrozenList[FrozenList["Cell"]] = FrozenList(FrozenList([]))
    row_data: FrozenList[FrozenList["Cell"]] = FrozenList(FrozenList([]))
    _columns: Optional[int | str | FrozenList[str]] = None
    _rows: Optional[int | str | FrozenList[str]] = None
    _stroke: Optional[str | FrozenList[str] | frozendict[str, str]] = None
    _align: Optional[str | FrozenList[str]] = None
    _lines: list["TableLine"] = None

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> "Table":
        table = cls()
        table.header_data = _parse_index(df.columns, direction="cols")
        table.index_data = _parse_index(df.index, direction="rows")
        row_data = FrozenList([])
        for _, *row in df.itertuples():
            row = FrozenList([Cell(value) for value in row])
            row.freeze()
            row_data.append(row)
        row_data.freeze()
        table.row_data = row_data
        table.columns = len(df.columns) + df.index.nlevels

        return table

    @property
    def columns(self):
        return self._columns

    @columns.setter
    def columns(self, value):
        if not isinstance(value, (int, str, list)):
            raise ValueError("Columns must be an integer, string, or list of strings")
        elif isinstance(value, list) and not all(isinstance(v, str) for v in value):
            raise ValueError("All elements in the list must be strings")
        elif isinstance(value, int) and not value == (
            len(self.row_data[0]) + len(self.index_data)
        ):
            raise ValueError(
                "Number of columns must match the number "
                "of table columns plus index levels"
            )
        elif isinstance(value, list) and not len(value) == (
            len(self.row_data[0]) + len(self.index_data)
        ):
            raise ValueError(
                "If specifying columns as a list, "
                "its length must match the number of table columns plus index levels"
            )
        if isinstance(value, list):
            self._columns = FrozenList(value)
            self._columns.freeze()
        else:
            self._columns = value

    @property
    def rows(self):
        return self._rows

    @rows.setter
    def rows(self, value):
        if not isinstance(value, (int, str, list)) and value is not None:
            raise ValueError(
                "Rows must be an integer, string, list of strings, or None"
            )
        elif isinstance(value, list) and not all(isinstance(v, str) for v in value):
            raise ValueError("All elements in the list must be strings")
        elif isinstance(value, int) and not value == (
            len(self.row_data) + len(self.header_data)
        ):
            raise ValueError(
                "Number of rows must match the number of table rows plus header levels"
            )
        elif isinstance(value, list) and not len(value) == (
            len(self.row_data) + len(self.header_data)
        ):
            raise ValueError(
                "If specifying rows as a list, "
                "its length must match the number of table rows plus header levels"
            )

        if isinstance(value, list):
            self._rows = FrozenList(value)
            self._rows.freeze()
        else:
            self._rows = value

    @property
    def stroke(self) -> Optional[str | FrozenList[str] | frozendict[str, str]]:
        return self._stroke

    @stroke.setter
    def stroke(self, value: Optional[str | FrozenList[str] | dict[str, str]]) -> None:
        if not isinstance(value, (str, list, dict)) and value is not None:
            raise ValueError(
                "Stroke must be a string, list of strings, dictionary, or None"
            )
        elif isinstance(value, list) and not all(isinstance(v, str) for v in value):
            raise ValueError("All elements in the list must be strings")
        elif isinstance(value, dict) and not all(
            isinstance(k, str) and isinstance(v, str) for k, v in value.items()
        ):
            raise ValueError("All keys and values in the dictionary must be strings")

        if isinstance(value, list):
            self._stroke = FrozenList(value)
            self._stroke.freeze()
        elif isinstance(value, dict):
            self._stroke = frozendict(value)
        elif value is None:
            self._stroke = "none"  # disables stroke in Typst
        else:
            self._stroke = value

    @property
    def align(self) -> Optional[str | FrozenList[str]]:
        return self._align

    @align.setter
    def align(self, value: Optional[str | list[str]]) -> None:
        if not isinstance(value, (str, list)) and value is not None:
            raise ValueError("Stroke must be a string, list of strings, or None")
        elif isinstance(value, list) and not all(isinstance(v, str) for v in value):
            raise ValueError("All elements in the list must be strings")
        if isinstance(value, list):
            self._align = FrozenList(value)
            self._align.freeze()
        else:
            self._align = value

    def add_hline(
        self,
        y: int,
        start: Optional[int] = None,
        end: Optional[int] = None,
        stroke: Optional[str] = None,
        position: Optional[Literal["start", "end"]] = None,
    ):
        self._add_line(TableLine(y, "horizontal", start, end, stroke, position))

    def add_vline(
        self,
        x: int,
        start: Optional[int] = None,
        end: Optional[int] = None,
        stroke: Optional[str] = None,
        position: Optional[Literal["start", "end"]] = None,
    ):
        self._add_line(TableLine(x, "vertical", start, end, stroke, position))

    def _add_line(self, line: "TableLine") -> None:
        if self._lines is None:
            self._lines = []
        self._lines.append(line)

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
            + self._render_lines()
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
        if self._columns is not None:
            columns = render_arg(self._columns)
            args.append(f"columns: {columns}")
        if self._rows is not None:
            rows = render_arg(self._rows)
            args.append(f"rows: {rows}")
        if self._stroke is not None:
            stroke = render_arg(self._stroke)
            args.append(f"stroke: {stroke}")
        if self._align is not None:
            align = render_arg(self._align)
            args.append(f"align: {align}")
        rendered_args = ",\n".join(args) + ",\n"

        return rendered_args

    def _render_lines(self) -> str:
        if not self._lines:
            rendered_lines = ""
        else:
            rendered_lines = ",\n".join(line.render() for line in self._lines) + ",\n"

        return rendered_lines

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


@dataclass
class TableLine:
    pos: int
    orientation: Literal["horizontal", "vertical"]
    start: Optional[int] = None
    end: Optional[int] = None
    stroke: Optional[str | dict[str, str]] = None
    position: Optional[Literal["start", "end"]] = None

    def render(self) -> str:
        args = []
        if self.orientation == "horizontal":
            line = "table.hline({0})"
            args.append(f"y: {self.pos}")
        else:
            line = "table.vline({0})"
            args.append(f"x: {self.pos}")

        if self.start is not None:
            args.append(f"start: {self.start}")
        if self.end is not None:
            args.append(f"end: {self.end}")
        if self.stroke is not None:
            stroke = self.stroke
            if isinstance(self.stroke, dict):
                stroke = render_mapping(self.stroke)
            args.append(f"stroke: {stroke}")
        if self.position is not None:
            args.append(f"position: {self.position}")
        line = line.format(", ".join(args))

        return line


def _parse_index(
    index: Union[pd.Index, pd.MultiIndex], direction: Literal["rows", "cols"]
) -> FrozenList[FrozenList["Cell"]]:
    headers: list[list[Cell]]
    if index.empty:
        headers = [[]]
    elif isinstance(index, pd.MultiIndex):
        headers = _parse_multi_index(index, direction)
    else:
        headers = [[Cell(header, colspan=1) for header in index]]

    frozen_headers = FrozenList(FrozenList(header) for header in headers)
    for header in frozen_headers:
        header.freeze()
    frozen_headers.freeze()

    return frozen_headers


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
