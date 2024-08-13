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
        if isinstance(self.elements, list):
            if any(not isinstance(e, (Renderable, str)) for e in self.elements):
                raise ValueError("Encountered invalid element type in elements list")
            if any(isinstance(e, Document) for e in self.elements):
                raise ValueError("Document cannot be added as it needs to be top-level")
        else:
            raise ValueError(f"Invalid elements type {type(self.elements)}")

    def add(self, element: Renderable | str) -> None:
        if not isinstance(element, (Renderable, str)):
            raise ValueError(f"Invalid element type: {type(element)}")
        if isinstance(element, Document):
            raise ValueError("Document cannot be added as it needs to be top-level")
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
            rendered = self._render_functional(args, self.elements)
        else:
            rendered = self._render_markdown(self.elements)

        return rendered

    def _render_functional(
        self, args: list[str], elements: list[Renderable | str]
    ) -> str:
        body = []
        for e in elements:
            b = utils.render(e)
            b = f"\n{b}\n" if isinstance(e, Itemize) else b.strip('"')
            body.append(f"[{b}]")
        rendered = ",\n".join(itertools.chain(args, body)).replace("\n", "\n  ")
        rendered = f"#list(\n  {rendered}\n)"

        return rendered

    def _render_markdown(self, elements: list[Renderable | str]) -> str:
        body = []
        for e in elements:
            b = utils.render(e)
            if isinstance(e, Itemize):
                b = b.replace("\n", "\n  ")
                b = "  " + b
            else:
                b = b.strip('"')
                b = f"- {b}"
            body.append(b)
        rendered = "\n".join(body)

        return rendered
