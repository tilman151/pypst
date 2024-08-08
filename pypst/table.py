from typing import Any, Optional, Union

import pandas as pd


class Table:
    def __init__(self) -> None:
        self.headers = []
        self.index = []
        self.rows = []

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> "Table":
        return cls()

    def _parse_headers(self, columns: Union[pd.Index, pd.MultiIndex]) -> list["Cell"]:
        if isinstance(columns, pd.MultiIndex):
            headers = self._parse_multiheader(columns)
        else:
            headers = [Cell(header, colspan=1) for header in columns]

        return headers

    def _parse_multiheader(self, columns: pd.MultiIndex) -> list["Cell"]:
        headers = []
        for level, level_codes in enumerate(columns.codes):
            colspan = 0
            prev_code = level_codes[0]
            for code in level_codes:
                header_name = columns.levels[level][code]
                if code == prev_code:
                    colspan += 1
                else:
                    headers.append(Cell(header_name, colspan=colspan))
                    prev_code = code
                    colspan = 0
            headers.append(Cell(header_name, colspan=colspan))
            headers.append(Cell())
        headers.pop()

        return headers


class Cell:
    def __init__(self, value: Optional[Any] = None, rowspan: int = 1,
                 colspan: int = 1) -> None:
        self.value = value

    def __str__(self) -> str:
        return "[]" if self.value is None else f"[{self.value}]"
