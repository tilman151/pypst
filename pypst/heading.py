from dataclasses import dataclass, field

from pypst.document import Document
from pypst.renderable import Renderable
from pypst.utils import Function, dataclass_fields_to_render, render


@dataclass
class Heading(Function):
    """
    A Heading element.

    If only the body and level are provided,
    the heading will be rendered as in Markdown.
    If any other attribute is provided, the heading will be rendered as a function.

    Args:
        body: The content of the heading.
        level: The absolute nesting depth of the heading, starting from one.
        depth: The relative nesting depth of the heading, starting from one.
        offset: The starting offset of each heading's level,
                used to turn its relative depth into its absolute level.
        numbering: The numbering scheme, for example, `"1.1"`.
        supplement: The supplement for the heading.
        outlined: Whether the heading appears in the outline.
        bookmarked: Whether the heading appears as a bookmark in PDF.

    Examples:
        >>> h = Heading("Heading 1", level=1)
        >>> print(h.render())
        = Heading 1

        >>> h = Heading("Heading 1", level=3)
        >>> print(h.render())
        === Heading 1

        >>> h = Heading('"Heading 1"', depth=2, offset=1)
        >>> print(h.render())
        #heading("Heading 1", depth: 2, offset: 1)
    """

    __is_function__ = True

    body: Renderable | str = field(metadata={"positional": True})
    level: int | None = None
    depth: int | None = None
    offset: int | None = None
    numbering: str | None = None
    supplement: Renderable | str | None = None
    outlined: bool | None = None
    bookmarked: bool | None = None

    def __post_init__(self) -> None:
        if self.level is not None and self.level < 1:
            raise ValueError("Level must be greater than 0")
        if self.depth is not None and self.depth < 1:
            raise ValueError("Depth must be greater than 0")
        if self.offset is not None and self.offset < 0:
            raise ValueError("Offset must be greater than or equal to 0")
        if (
            self.depth is not None or self.offset is not None
        ) and self.level is not None:
            raise ValueError("Level cannot be set if depth or offset is set")
        if not isinstance(self.body, (Renderable, str)):
            raise ValueError(f"Invalid body type: {type(self.body)}")
        if isinstance(self.body, Document):
            raise ValueError(
                "Document cannot be set as body, because it needs to be top-level"
            )

    def render(self) -> str:
        """
        Render the heading to a string.

        If only body and level are provided,
        the heading will be rendered as in Markdown.
        If any other attribute is provided, the heading will be rendered as a function.

        Returns:
            The rendered heading element.
        """
        if self.level is not None and len(list(dataclass_fields_to_render(self))) == 2:
            # remove unnecessary quotes, because Markdown style is not in code mode
            body = render(self.body).strip('"')
            return f"{'=' * self.level} {body}"
        else:
            return super().render()
