from dataclasses import dataclass
from typing import Optional

from pypst import utils
from pypst.document import Document
from pypst.renderable import Renderable


@dataclass
class Figure:
    body: Renderable | str

    placement: Optional[str] = None
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
