from dataclasses import dataclass
from typing import Optional, Literal

from pypst import utils
from pypst.document import Document
from pypst.renderable import Renderable


@dataclass
class Figure:
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
        #figure(
          [Hello, World!],
          caption: [This is content.]
        )

        >>> from pypst import Image
        >>> fig = Figure(Image("image.png"), caption="[This is an image.]")
        >>> print(fig.render())
        #figure(
          image("image.png"),
          caption: [This is an image.]
        )
    """

    body: Renderable | str

    placement: Optional[Literal["auto", "top", "bottom"]] = None
    caption: Optional[str] = None
    kind: Optional[str] = None
    supplement: Optional[str] = None
    numbering: Optional[str] = None
    gap: Optional[str] = None
    outlined: Optional[bool] = None

    def __post_init__(self) -> None:
        if not isinstance(self.body, (Renderable, str)):
            raise ValueError(f"Invalid body type: {type(self.body)}")
        elif isinstance(self.body, Document):
            raise ValueError(
                "Document cannot be set as body, because it needs to be top-level"
            )

    def render(self) -> str:
        """
        Render the figure.

        The body and attributes of the figure is indented by two spaces.

        Returns:
            The rendered figure.
        """
        # remove the leading '#' because we're in code mode
        args = [utils.render(self.body).lstrip("#")]
        if self.placement is not None:
            args.append(f"placement: {self.placement}")
        if self.caption is not None:
            args.append(f"caption: {self.caption}")
        if self.kind is not None:
            args.append(f"kind: {self.kind}")
        if self.supplement is not None:
            args.append(f"supplement: {self.supplement}")
        if self.numbering is not None:
            args.append(f"numbering: {self.numbering}")
        if self.gap is not None:
            args.append(f"gap: {self.gap}")
        if self.outlined is not None:
            args.append(f"outlined: {'true' if self.outlined else 'false'}")

        # indent body and args by 2 spaces
        inner = ",\n".join(args).replace("\n", "\n  ")

        return "#figure(\n  {0}\n)".format(inner)
