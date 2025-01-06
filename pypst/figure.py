from dataclasses import dataclass, field
from typing import Literal

from pypst.document import Document
from pypst.renderable import Renderable
from pypst.utils import Function


@dataclass
class Figure(Function):
    """
    A figure is a block element that contains another element.

    It can be used to add captions, numbering, and other metadata to the element.

    Args:
        body: The element to be rendered inside the figure.
        placement: The placement of the figure.
        caption: The caption of the figure.
        kind: The kind of the figure.
        supplement: The supplement of the figure added when the figure is referenced.
        numbering: The numbering scheme of the figure.
        gap: The gap between body and caption.
        outlined: Whether the figure is added to the outline.

    Examples:
        >>> fig = Figure("[Hello, World!]", caption="[This is content.]")
        >>> print(fig.render())
        #figure([Hello, World!], caption: [This is content.])

        >>> from pypst import Image
        >>> fig = Figure(Image("image.png"), caption="[This is an image.]")
        >>> print(fig.render())
        #figure(image("image.png"), caption: [This is an image.])
    """

    __is_function__ = True

    body: Renderable | str = field(metadata={"positional": True})

    placement: Literal["auto", "top", "bottom"] | None = None
    caption: Renderable | str | None = None
    kind: Renderable | str | None = None
    supplement: Renderable | str | None = None
    numbering: Renderable | str | None = None
    gap: Renderable | str | None = None
    outlined: bool | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.body, (Renderable, str)):
            raise ValueError(f"Invalid body type: {type(self.body)}")
        elif isinstance(self.body, Document):
            raise ValueError(
                "Document cannot be set as body, because it needs to be top-level"
            )
