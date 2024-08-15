from typing import Optional, Any

from pypst.utils import render_mapping, render_sequence


class Cell:
    """
    A cell element that can be rendered as a table cell.

    Normally, the user does not need to create a cell directly.
    When creating a table from a data frame, the table will automatically create cells.
    These cells can then be modified to style them individually.

    Args:
        value: The content of the cell.
        rowspan: The number of rows the cell spans.
        colspan: The number of columns the cell spans.
        fill: The background color of the cell.
        align: The alignment of the cell content.
        stroke: The stroke style of the cell.

    Examples:
        >>> cell = Cell(
        ...     "Value",
        ...     rowspan=2,
        ...     colspan=3,
        ...     fill="red",
        ...     align="center",
        ...     stroke="black"
        ... )
        >>> print(cell)
        [#table.cell(rowspan: 2, colspan: 3, fill: red, align: center, stroke: black)[Value]]
    """

    def __init__(
        self,
        value: Optional[Any] = None,
        rowspan: int = 1,
        colspan: int = 1,
        fill: Optional[str] = None,
        align: Optional[str] = None,
        stroke: Optional[str | list | dict] = None,
    ) -> None:
        self.value = value
        self.rowspan = rowspan
        self.colspan = colspan
        self.fill = fill
        self.align = align
        self.stroke = stroke

    def __str__(self) -> str:
        return self.render()

    def __repr__(self) -> str:
        return (
            f"Cell(value={self.value}, rowspan={self.rowspan}, colspan={self.colspan}, "
            f"fill={self.fill}, align={self.align}, stroke={self.stroke})"
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Cell):
            return False

        return (
            self.value == other.value
            and self.rowspan == other.rowspan
            and self.colspan == other.colspan
            and self.fill == other.fill
            and self.align == other.align
            and self.stroke == other.stroke
        )

    def render(self) -> str:
        """
        Render the cell to string.

        The cell function is surrounded by a content block to fit the table syntax.

        Returns:
            The rendered cell.
        """
        args = []
        if self.rowspan > 1:
            args.append(f"rowspan: {self.rowspan}")
        if self.colspan > 1:
            args.append(f"colspan: {self.colspan}")
        if self.fill is not None:
            args.append(f"fill: {self.fill}")
        if self.align is not None:
            args.append(f"align: {self.align}")
        if self.stroke is not None:
            stroke = self.stroke
            if isinstance(self.stroke, dict):
                stroke = render_mapping(self.stroke)
            elif isinstance(self.stroke, list):
                stroke = render_sequence(self.stroke)
            args.append(f"stroke: {stroke}")

        cell = "[]" if self.value is None else f"[{self.value}]"
        if args:
            cell = f"[#table.cell({', '.join(args)}){cell}]"

        return cell
