import itertools
from dataclasses import dataclass
from typing import Optional

from pypst import utils
from pypst.document import Document
from pypst.renderable import Renderable


@dataclass
class Itemize:
    """
    An element that represents a bullet point list.

    If no arguments are provided, the list will be rendered as a Markdown list.
    Otherwise, the list will be rendered as a function.
    It is possible to nest lists in both Markdown and functional forms.

    Args:
        elements: List of elements to be rendered as bullet points.
        tight: Whether to use list or leading spacing between elements.
        marker: The bullet point markers to use.
        indent: The indent for each element.
        body_indent: The spacing between the marker and the element body.
        spacing: The spacing of a non-tight list.

    Examples:
        >>> itemize = Itemize(["First", "Second"])
        >>> print(itemize.render())
        - First
        - Second

        >>> itemize = Itemize(["First", "Second"], tight=True)
        >>> print(itemize.render())
        #list(
          tight: true,
          [First],
          [Second]
        )

        >>> itemize = Itemize(["First", Itemize(["Nested 1", "Nested 2"]), "Second"])
        >>> print(itemize.render())
        - First
          - Nested 1
          - Nested 2
        - Second

        >>> enumerate = Itemize(["First", Enumerate(["Nested 1", "Nested 2"]), "Second"])
        >>> print(enumerate.render())
        - First
          + Nested 1
          + Nested 2
        - Second

        >>> itemize = Itemize([])
        >>> itemize.add("First")
        >>> itemize.add("Second")
        >>> print(itemize.render())
        - First
        - Second
    """

    elements: list[Renderable | str]
    tight: Optional[bool] = None
    marker: Optional[str | list[str]] = None
    indent: Optional[str] = None
    body_indent: Optional[str] = None
    spacing: Optional[str] = None

    def __post_init__(self) -> None:
        _check_elements(self.elements)

    def add(self, element: Renderable | str) -> None:
        """
        Add an element to the bullet point list.

        Args:
            element: The new element.
        """
        _check_element(element)
        self.elements.append(element)

    def render(self) -> str:
        """
        Render the bullet point list to string.

        If any arguments are provided, the list will be rendered as a function.
        Otherwise, the list will be rendered as a Markdown list.

        Returns:
            The rendered list.
        """
        args = []
        if self.tight:
            args.append(f"tight: {utils.render(self.tight)}")
        if self.marker:
            args.append(f"marker: {utils.render(self.marker)}")
        if self.indent:
            args.append(f"indent: {self.indent}")
        if self.body_indent:
            args.append(f"body-indent: {self.body_indent}")
        if self.spacing:
            args.append(f"spacing: {self.spacing}")

        if args:
            rendered = _render_functional(args, self.elements, "list")
        else:
            rendered = _render_markdown(self.elements, "-")

        return rendered


@dataclass
class Enumerate:
    """
    An element that represents a numbered list.

    If no arguments are provided, the list will be rendered as a Markdown list.
    Otherwise, the list will be rendered as a function.
    It is possible to nest lists in both Markdown and functional forms.

    Args:
        elements: List of elements to be rendered as numbered points.
        tight: Whether to use list or leading spacing between elements.
        numbering: The numbering scheme to use.
        start: The starting number for the list.
        full: Whether to use full numbering with parent enumerations.
        indent: The indent for each element.
        body_indent: The spacing between the number and the element body.
        spacing: The spacing of a non-tight list.
        number_align: The alignment of the numbers.

    Examples:
        >>> enumerate = Enumerate(["First", "Second"])
        >>> print(enumerate.render())
        + First
        + Second

        >>> enumerate = Enumerate(["First", Enumerate(["Nested 1", "Nested 2"]), "Second"])
        >>> print(enumerate.render())
        + First
          + Nested 1
          + Nested 2
        + Second

        >>> enumerate = Enumerate(["First", Itemize(["Nested 1", "Nested 2"]), "Second"])
        >>> print(enumerate.render())
        + First
          - Nested 1
          - Nested 2
        + Second

        >>> enumerate = Enumerate([])
        >>> enumerate.add("First")
        >>> enumerate.add("Second")
        >>> print(enumerate.render())
        + First
        + Second
    """

    elements: list[Renderable | str]
    tight: Optional[bool] = None
    numbering: Optional[str] = None
    start: Optional[int] = None
    full: Optional[bool] = None
    indent: Optional[str] = None
    body_indent: Optional[str] = None
    spacing: Optional[str] = None
    number_align: Optional[str] = None

    def __post_init__(self) -> None:
        _check_elements(self.elements)

    def add(self, element: Renderable | str) -> None:
        """
        Add an element to the numbered list.

        Args:
            element: The new element.
        """
        _check_element(element)
        self.elements.append(element)

    def render(self) -> str:
        """
        Render the numbered list to string.

        If any arguments are provided, the list will be rendered as a function.
        Otherwise, the list will be rendered as a Markdown list.

        Returns:
            The rendered numbered list.
        """
        args = []
        if self.tight:
            args.append(f"tight: {utils.render(self.tight)}")
        if self.numbering:
            args.append(f"numbering: {self.numbering}")
        if self.start:
            args.append(f"start: {self.start}")
        if self.full:
            args.append(f"full: {utils.render(self.full)}")
        if self.indent:
            args.append(f"indent: {self.indent}")
        if self.body_indent:
            args.append(f"body-indent: {self.body_indent}")
        if self.spacing:
            args.append(f"spacing: {self.spacing}")
        if self.number_align:
            args.append(f"number-align: {self.number_align}")

        if args:
            rendered = _render_functional(args, self.elements, "enum")
        else:
            rendered = _render_markdown(self.elements, "+")

        return rendered


def _check_elements(elements: list[Renderable | str]) -> None:
    if isinstance(elements, list):
        if any(not isinstance(e, (Renderable, str)) for e in elements):
            raise ValueError("Encountered invalid element type in elements list")
        if any(isinstance(e, Document) for e in elements):
            raise ValueError("Document cannot be added as it needs to be top-level")
    else:
        raise ValueError(f"Invalid elements type {type(elements)}")


def _check_element(element: Renderable | str) -> None:
    if not isinstance(element, (Renderable, str)):
        raise ValueError(f"Invalid element type: {type(element)}")
    if isinstance(element, Document):
        raise ValueError("Document cannot be added as it needs to be top-level")


def _render_functional(
    args: list[str], elements: list[Renderable | str], function_name: str
) -> str:
    body = []
    for e in elements:
        b = utils.render(e)
        b = f"\n{b}\n" if isinstance(e, (Itemize, Enumerate)) else b.strip('"')
        body.append(f"[{b}]")
    rendered = ",\n".join(itertools.chain(args, body)).replace("\n", "\n  ")
    rendered = f"#{function_name}(\n  {rendered}\n)"

    return rendered


def _render_markdown(elements: list[Renderable | str], prefix: str) -> str:
    body = []
    for e in elements:
        b = utils.render(e)
        if isinstance(e, (Itemize, Enumerate)):
            b = b.replace("\n", "\n  ")
            b = "  " + b
        else:
            b = b.strip('"')
            b = f"{prefix} {b}"
        body.append(b)
    rendered = "\n".join(body)

    return rendered
