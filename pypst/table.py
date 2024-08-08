from typing import Any, Optional, Union

import pandas as pd


class Table:
    def __init__(self) -> None:
        self.headers = []
        self.index = []
        self.rows = []

        self.num_columns = 0
        self.num_rows = 0

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> "Table":
        table = cls()
        table.headers = _parse_index(df.columns)
        table.num_columns = len(df.columns)

        return table

    def __str__(self) -> str:
        return self.render()

    def render(self) -> str:
        table = "table.header" + "".join(header.render() for header in self.headers)
        table = f"#table(\ncolumns: {self.num_columns},\n{table}\n)"

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


def _parse_index(columns: Union[pd.Index, pd.MultiIndex]) -> list["Cell"]:
    if columns.empty:
        headers = []
    elif isinstance(columns, pd.MultiIndex):
        headers = _parse_multi_index(columns)
    else:
        headers = [Cell(header, colspan=1) for header in columns]

    return headers


def _parse_multi_index(columns: pd.MultiIndex) -> list["Cell"]:
    assert not columns.empty
    headers = []
    for level, level_codes in enumerate(columns.codes):
        colspan = 0
        prev_code = level_codes[0]
        for code in level_codes:
            header_name = columns.levels[level][code]
            if code == prev_code:
                colspan += 1
            else:
                headers.append(Cell(columns.levels[level][prev_code], colspan=colspan))
                prev_code = code
                colspan = 1
        headers.append(Cell(header_name, colspan=colspan))

    return headers
