import itertools
from dataclasses import dataclass
from typing import Optional

from pypst import utils
from pypst.document import Document
from pypst.renderable import Renderable


@dataclass
class Itemize:
    elements: list[Renderable | str]
    tight: Optional[bool] = None
    marker: Optional[str | list[str]] = None
    indent: Optional[str] = None
    body_indent: Optional[str] = None
    spacing: Optional[str] = None

    def __post_init__(self) -> None:
        _check_elements(self.elements)

    def add(self, element: Renderable | str) -> None:
        _check_element(element)
        self.elements.append(element)

    def render(self) -> str:
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
        _check_element(element)
        self.elements.append(element)

    def render(self) -> str:
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
