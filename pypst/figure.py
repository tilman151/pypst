from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class Figure:
    body: Any

    placement: Optional[str] = None
    caption: Optional[str] = None
    kind: Optional[str] = None
    supplement: Optional[str] = None
    numbering: Optional[str] = None
    gap: Optional[str] = None
    outlined: Optional[bool] = None

    def render(self) -> str:
        # remove the leading '#' because we're in code mode
        args = [self.body.render().lstrip("#")]
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
