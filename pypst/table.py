import itertools
from dataclasses import dataclass
from typing import Optional, Union, Literal

try:
    import pandas as pd
except ImportError:
    raise ModuleNotFoundError(
        "Could not find Pandas. To use the table functionality, Pypst needs to be installed as 'pypst[pandas]'."
    )
from frozendict import frozendict

from frozenlist import FrozenList

from pypst.cell import Cell
from pypst.utils import render_type, render_mapping


@dataclass
class Table:
    """
    A table element.

    A table is constructed from a pandas DataFrame using the [from_dataframe][pypst.table.Table.from_dataframe] method.
    Afterward, styling options can be set using the properties of the class.
    Manual horizontal and vertical lines can be added using the
    `add_hline` and `add_vline` methods.

    Most properties that accept a string also accept functions in Typst.
    Typst functions can be supplied in string form,
    for example, `"(x, y) => if x > y then {red} else {black}"`.

    Hint:
        The header, index and row data can be accessed via the `header_data`,
        `index_data` and `row_data` properties.
        The lists can't be modified directly,
        but the elements can be accessed to apply styling to individual cells.
    """

    header_data: FrozenList[FrozenList["Cell"]] = FrozenList(FrozenList([]))
    index_data: FrozenList[FrozenList["Cell"]] = FrozenList(FrozenList([]))
    row_data: FrozenList[FrozenList["Cell"]] = FrozenList(FrozenList([]))
    _columns: Optional[int | str | FrozenList[str]] = None
    _rows: Optional[int | str | FrozenList[str]] = None
    _stroke: Optional[str | FrozenList[str] | frozendict[str, str]] = None
    _align: Optional[str | FrozenList[str]] = None
    _fill: Optional[str | FrozenList[str]] = None
    _gutter: Optional[int | str | FrozenList[str]] = None
    _column_gutter: Optional[int | str | FrozenList[str]] = None
    _row_gutter: Optional[int | str | FrozenList[str]] = None
    _lines: Optional[list["TableLine"]] = None

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> "Table":
        """
        Create a new table element from a Pandas DataFrame.

        The `columns` property of the data frame will be used as the header data and
        the `index` property will be used as the index data.
        The header is rendered as the `table.header` element and the index as the
        first columns in each row.
        Multi-level indexes are supported.

        After creating the table, styling options can be set using the properties of
        the table class.

        Args:
            df: The DataFrame to create the table from.

        Examples:
            >>> df = pd.DataFrame({"A": [1, 2], "B": [3, 4]}, index=["X", "Y"])
            >>> table = Table.from_dataframe(df)
            >>> print(table.render())
            #table(
              columns: 3,
              table.header[][A][B],
              [X], [1], [3],
              [Y], [2], [4]
            )

            >>> df = pd.DataFrame(
            ...     [[1, 3], [2, 4]],
            ...     columns=pd.MultiIndex.from_tuples([("A", "mean"), ("A", "std")]),
            ...     index=["X", "Y"]
            ... )
            >>> table = Table.from_dataframe(df)
            >>> print(table.render())
            #table(
              columns: 3,
              table.header[#table.cell(rowspan: 2)[]][#table.cell(colspan: 2)[A]][mean][std],
              [X], [1], [3],
              [Y], [2], [4]
            )

            >>> df = pd.DataFrame(
            ...     [[1, 3], [2, 4]],
            ...     columns=["A", "B"],
            ...     index=pd.MultiIndex.from_tuples([("X", "mean"), ("X", "std")])
            ... )
            >>> table = Table.from_dataframe(df)
            >>> print(table.render())
            #table(
              columns: 4,
              table.header[#table.cell(colspan: 2)[]][A][B],
              [#table.cell(rowspan: 2)[X]], [mean], [1], [3],
              [std], [2], [4]
            )

        Returns:
            The new table element.
        """
        table = cls()
        table.header_data = _parse_index(df.columns, direction="cols")
        table.index_data = _parse_index(df.index, direction="rows")
        row_data: FrozenList[FrozenList[Cell]] = FrozenList([])
        for _, *row in df.itertuples():
            row_cells = FrozenList([Cell(value) for value in row])
            row_cells.freeze()
            row_data.append(row_cells)
        row_data.freeze()
        table.row_data = row_data
        table.columns = len(df.columns) + df.index.nlevels

        return table

    @property
    def columns(self) -> Optional[int | str | FrozenList[str]]:
        """
        The number of columns or column styling array.

        This property is automatically set when creating a table from a DataFrame.
        It can be replaced by an integer to apply styling to all columns or by a list
        to apply styling to individual columns.

        If a list is provided, it must have the same length as the number of columns
        plus the number of index levels.

        Examples:
            >>> df = pd.DataFrame({"A": [1, 2], "B": [3, 4]}, index=["X", "Y"])
            >>> table = Table.from_dataframe(df)
            >>> table.columns = "50%"
            >>> print(table.render())
            #table(
              columns: 50%,
              table.header[][A][B],
              [X], [1], [3],
              [Y], [2], [4]
            )

            >>> df = pd.DataFrame({"A": [1, 2], "B": [3, 4]}, index=["X", "Y"])
            >>> table = Table.from_dataframe(df)
            >>> table.columns = ["10pt", "20pt", "30pt"] # two columns plus index
            >>> print(table.render())
            #table(
              columns: (10pt, 20pt, 30pt),
              table.header[][A][B],
              [X], [1], [3],
              [Y], [2], [4]
            )
        """
        return self._columns

    @columns.setter
    def columns(self, value: int | str | list[str]) -> None:
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
    def rows(self) -> Optional[int | str | FrozenList[str]]:
        """
        The number of rows or row styling array.

        This property is automatically set when creating a table from a DataFrame.
        It can be replaced by an integer to apply styling to all rows or by a list
        to apply styling to individual rows.

        If a list is provided, it must have the same length as the number of rows
        plus the number of header levels.

        Examples:
            >>> df = pd.DataFrame({"A": [1, 2], "B": [3, 4]}, index=["X", "Y"])
            >>> table = Table.from_dataframe(df)
            >>> table.rows = "50%"
            >>> print(table.render())
            #table(
              columns: 3,
              rows: 50%,
              table.header[][A][B],
              [X], [1], [3],
              [Y], [2], [4]
            )

            >>> df = pd.DataFrame({"A": [1, 2], "B": [3, 4]}, index=["X", "Y"])
            >>> table = Table.from_dataframe(df)
            >>> table.rows = ["10pt", "20pt", "30pt"] # two rows plus header
            >>> print(table.render())
            #table(
              columns: 3,
              rows: (10pt, 20pt, 30pt),
              table.header[][A][B],
              [X], [1], [3],
              [Y], [2], [4]
            )
        """
        return self._rows

    @rows.setter
    def rows(self, value: int | str | list[str]) -> None:
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
        """
        The stroke style for the table cells.

        This can be either a string to style all cells,
        a list of strings to style each column,
        or a dictionary to control the stroke of each of the cells' sides.

        Examples:
            >>> df = pd.DataFrame({"A": [1, 2], "B": [3, 4]}, index=["X", "Y"])
            >>> table = Table.from_dataframe(df)
            >>> table.stroke = "2pt"
            >>> print(table.render())
            #table(
              columns: 3,
              stroke: 2pt,
              table.header[][A][B],
              [X], [1], [3],
              [Y], [2], [4]
            )

            >>> df = pd.DataFrame({"A": [1, 2], "B": [3, 4]}, index=["X", "Y"])
            >>> table = Table.from_dataframe(df)
            >>> table.stroke = ["2pt", "1pt", "3pt"]
            >>> print(table.render())
            #table(
              columns: 3,
              stroke: (2pt, 1pt, 3pt),
              table.header[][A][B],
              [X], [1], [3],
              [Y], [2], [4]
            )

            >>> df = pd.DataFrame({"A": [1, 2], "B": [3, 4]}, index=["X", "Y"])
            >>> table = Table.from_dataframe(df)
            >>> table.stroke = {"top": "2pt", "bottom": "1pt"}
            >>> print(table.render())
            #table(
              columns: 3,
              stroke: (top: 2pt, bottom: 1pt),
              table.header[][A][B],
              [X], [1], [3],
              [Y], [2], [4]
            )
        """
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
        else:
            self._stroke = value

    @property
    def align(self) -> Optional[str | FrozenList[str]]:
        """
        The alignment for the table columns.

        This can be either a string to align all columns,
        or a list of strings to align individual columns.

        Examples:
            >>> df = pd.DataFrame({"A": [1, 2], "B": [3, 4]}, index=["X", "Y"])
            >>> table = Table.from_dataframe(df)
            >>> table.align = "right"
            >>> print(table.render())
            #table(
              columns: 3,
              align: right,
              table.header[][A][B],
              [X], [1], [3],
              [Y], [2], [4]
            )

            >>> df = pd.DataFrame({"A": [1, 2], "B": [3, 4]}, index=["X", "Y"])
            >>> table = Table.from_dataframe(df)
            >>> table.align = ["left", "center", "right"]  # two columns plus index
            >>> print(table.render())
            #table(
              columns: 3,
              align: (left, center, right),
              table.header[][A][B],
              [X], [1], [3],
              [Y], [2], [4]
            )
        """
        return self._align

    @align.setter
    def align(self, value: Optional[str | list[str]]) -> None:
        if not isinstance(value, (str, list)) and value is not None:
            raise ValueError("Align must be a string, list of strings, or None")
        elif isinstance(value, list) and not all(isinstance(v, str) for v in value):
            raise ValueError("All elements in the align list must be strings")
        if isinstance(value, list):
            self._align = FrozenList(value)
            self._align.freeze()
        else:
            self._align = value

    @property
    def fill(self) -> Optional[str | FrozenList[str]]:
        """
        The background color for the table cells.

        This can be either a string to fill all cells,
        or a list of strings to fill individual columns.

        Examples:
            >>> df = pd.DataFrame({"A": [1, 2], "B": [3, 4]}, index=["X", "Y"])
            >>> table = Table.from_dataframe(df)
            >>> table.fill = "red"
            >>> print(table.render())
            #table(
              columns: 3,
              fill: red,
              table.header[][A][B],
              [X], [1], [3],
              [Y], [2], [4]
            )

            >>> df = pd.DataFrame({"A": [1, 2], "B": [3, 4]}, index=["X", "Y"])
            >>> table = Table.from_dataframe(df)
            >>> table.fill = ["red", "blue", "green"]  # two columns plus index
            >>> print(table.render())
            #table(
              columns: 3,
              fill: (red, blue, green),
              table.header[][A][B],
              [X], [1], [3],
              [Y], [2], [4]
            )
        """
        return self._fill

    @fill.setter
    def fill(self, value: Optional[str | list[str]]) -> None:
        if not isinstance(value, (str, list)) and value is not None:
            raise ValueError("Fill must be a string, list of strings, or None")
        elif isinstance(value, list) and not all(isinstance(v, str) for v in value):
            raise ValueError("All elements in the fill list must be strings")
        if isinstance(value, list):
            self._fill = FrozenList(value)
            self._fill.freeze()
        else:
            self._fill = value

    @property
    def gutter(self) -> Optional[int | str | FrozenList[str]]:
        """
        The spacing between table cells.

        This can be either an integer/string to set the gutter for all cells,
        or a list of strings to set the gutter for individual columns.

        Examples:
            >>> df = pd.DataFrame({"A": [1, 2], "B": [3, 4]}, index=["X", "Y"])
            >>> table = Table.from_dataframe(df)
            >>> table.gutter = 10
            >>> print(table.render())
            #table(
              columns: 3,
              gutter: 10,
              table.header[][A][B],
              [X], [1], [3],
              [Y], [2], [4]
            )

            >>> df = pd.DataFrame({"A": [1, 2], "B": [3, 4]}, index=["X", "Y"])
            >>> table = Table.from_dataframe(df)
            >>> table.gutter = ["10pt", "20pt", "30pt"]  # two columns plus index
            >>> print(table.render())
            #table(
              columns: 3,
              gutter: (10pt, 20pt, 30pt),
              table.header[][A][B],
              [X], [1], [3],
              [Y], [2], [4]
            )
        """
        return self._gutter

    @gutter.setter
    def gutter(self, value: Optional[int | str | list[str]]) -> None:
        if not isinstance(value, (int | str, list)) and value is not None:
            raise ValueError("Gutter must be an int, string, list of strings, or None")
        elif isinstance(value, list) and not all(isinstance(v, str) for v in value):
            raise ValueError("All elements in the gutter list must be strings")
        if isinstance(value, list):
            self._gutter = FrozenList(value)
            self._gutter.freeze()
        else:
            self._gutter = value

    @property
    def column_gutter(self) -> Optional[int | str | FrozenList[str]]:
        """
        The spacing between table columns.

        This can be either an integer/string to set the column gutter for all columns,
        or a list of strings to set the column gutter for individual columns.

        Examples:
            >>> df = pd.DataFrame({"A": [1, 2], "B": [3, 4]}, index=["X", "Y"])
            >>> table = Table.from_dataframe(df)
            >>> table.column_gutter = 10
            >>> print(table.render())
            #table(
              columns: 3,
              column-gutter: 10,
              table.header[][A][B],
              [X], [1], [3],
              [Y], [2], [4]
            )

            >>> df = pd.DataFrame({"A": [1, 2], "B": [3, 4]}, index=["X", "Y"])
            >>> table = Table.from_dataframe(df)
            >>> table.column_gutter = ["10pt", "20pt", "30pt"]  # two columns plus index
            >>> print(table.render())
            #table(
              columns: 3,
              column-gutter: (10pt, 20pt, 30pt),
              table.header[][A][B],
              [X], [1], [3],
              [Y], [2], [4]
            )
        """
        return self._column_gutter

    @column_gutter.setter
    def column_gutter(self, value: Optional[int | str | list[str]]) -> None:
        if not isinstance(value, (int | str, list)) and value is not None:
            raise ValueError(
                "Column gutter must be an int, string, list of strings, or None"
            )
        elif isinstance(value, list) and not all(isinstance(v, str) for v in value):
            raise ValueError("All elements in the column gutter list must be strings")
        if isinstance(value, list):
            self._column_gutter = FrozenList(value)
            self._column_gutter.freeze()
        else:
            self._column_gutter = value

    @property
    def row_gutter(self) -> Optional[int | str | FrozenList[str]]:
        """
        The spacing between table rows.

        This can be either an integer/string to set the row gutter for all cells,
        or a list of strings to set the row gutter for individual columns.

        Examples:
            >>> df = pd.DataFrame({"A": [1, 2], "B": [3, 4]}, index=["X", "Y"])
            >>> table = Table.from_dataframe(df)
            >>> table.row_gutter = 10
            >>> print(table.render())
            #table(
              columns: 3,
              row-gutter: 10,
              table.header[][A][B],
              [X], [1], [3],
              [Y], [2], [4]
            )

            >>> df = pd.DataFrame({"A": [1, 2], "B": [3, 4]}, index=["X", "Y"])
            >>> table = Table.from_dataframe(df)
            >>> table.row_gutter = ["10pt", "20pt", "30pt"]  # two columns plus index
            >>> print(table.render())
            #table(
              columns: 3,
              row-gutter: (10pt, 20pt, 30pt),
              table.header[][A][B],
              [X], [1], [3],
              [Y], [2], [4]
            )
        """
        return self._row_gutter

    @row_gutter.setter
    def row_gutter(self, value: Optional[int | str | list[str]]) -> None:
        if not isinstance(value, (int | str, list)) and value is not None:
            raise ValueError(
                "Row gutter must be an int, string, list of strings, or None"
            )
        elif isinstance(value, list) and not all(isinstance(v, str) for v in value):
            raise ValueError("All elements in the row gutter list must be strings")
        if isinstance(value, list):
            self._row_gutter = FrozenList(value)
            self._row_gutter.freeze()
        else:
            self._row_gutter = value

    def add_hline(
        self,
        y: int,
        start: Optional[int] = None,
        end: Optional[int] = None,
        stroke: Optional[str] = None,
        position: Optional[Literal["start", "end"]] = None,
    ) -> None:
        """
        Add a horizontal line to the table at the specified row position.

        Args:
            y: The row position.
            start: The column to start the line.
            end: The column to end the line.
            stroke: The stroke style for the line.
            position: Whether the line should appear before or after the row.

        Examples:
            >>> df = pd.DataFrame({"A": [1, 2], "B": [3, 4]}, index=["X", "Y"])
            >>> table = Table.from_dataframe(df)
            >>> table.add_hline(1, stroke="2pt")
            >>> print(table.render())
            #table(
              columns: 3,
              table.hline(y: 1, stroke: 2pt),
              table.header[][A][B],
              [X], [1], [3],
              [Y], [2], [4]
            )
        """
        self._add_line(TableLine(y, "horizontal", start, end, stroke, position))

    def add_vline(
        self,
        x: int,
        start: Optional[int] = None,
        end: Optional[int] = None,
        stroke: Optional[str] = None,
        position: Optional[Literal["start", "end"]] = None,
    ) -> None:
        """
        Add a vertical line to the table at the specified column position.

        Args:
            x: The column position.
            start: The row to start the line.
            end: The row to end the line.
            stroke: The stroke style for the line.
            position: Whether the line should appear before or after the column.

        Examples:
            >>> df = pd.DataFrame({"A": [1, 2], "B": [3, 4]}, index=["X", "Y"])
            >>> table = Table.from_dataframe(df)
            >>> table.add_vline(1, stroke="2pt")
            >>> print(table.render())
            #table(
              columns: 3,
              table.vline(x: 1, stroke: 2pt),
              table.header[][A][B],
              [X], [1], [3],
              [Y], [2], [4]
            )
        """
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
        """
        Render the table element to a string.

        Vertical and horizontal lines are rendered before the table body.
        All attributes and the body are indented by two spaces.

        Returns:
            The rendered table element.
        """
        headers = itertools.chain(*self.header_data)
        index_placeholder = Cell(
            rowspan=len(self.header_data), colspan=len(self.index_data)
        )
        inner = (
            self._render_args()
            + self._render_lines()
            + "table.header"
            + index_placeholder.render()
            + "".join(header.render() for header in headers)
            + ",\n"
            + self._render_rows()
        )
        # indent body and args by 2 spaces
        table = "#table(\n  " + inner.replace("\n", "\n  ") + "\n)"

        return table

    def _render_args(self) -> str:
        args = []
        if self._columns is not None:
            columns = render_type(self._columns)
            args.append(f"columns: {columns}")
        if self._rows is not None:
            rows = render_type(self._rows)
            args.append(f"rows: {rows}")
        if self._stroke is not None:
            stroke = render_type(self._stroke)
            args.append(f"stroke: {stroke}")
        if self._align is not None:
            align = render_type(self._align)
            args.append(f"align: {align}")
        if self._fill is not None:
            fill = render_type(self._fill)
            args.append(f"fill: {fill}")
        if self._gutter is not None:
            gutter = render_type(self._gutter)
            args.append(f"gutter: {gutter}")
        if self._column_gutter is not None:
            column_gutter = render_type(self._column_gutter)
            args.append(f"column-gutter: {column_gutter}")
        if self._row_gutter is not None:
            row_gutter = render_type(self._row_gutter)
            args.append(f"row-gutter: {row_gutter}")
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
        table = table[:-2]  # remove trailing comma and newline

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
