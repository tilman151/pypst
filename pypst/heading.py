from dataclasses import dataclass
from typing import Optional

from pypst import utils
from pypst.document import Document
from pypst.renderable import Renderable


@dataclass
class Heading:
    body: Renderable | str
    level: Optional[int] = None
    depth: Optional[int] = None
    offset: Optional[int] = None
    numbering: Optional[str] = None
    supplement: Optional[Renderable | str] = None
    outlined: Optional[bool] = None
    bookmarked: Optional[bool] = None

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
        args = [utils.render(self.body)]
        if self.level is not None:
            args.append(f"level: {self.level}")
        if self.depth is not None:
            args.append(f"depth: {self.depth}")
        if self.offset is not None:
            args.append(f"offset: {self.offset}")
        if self.numbering is not None:
            args.append(f"numbering: {self.numbering}")
        if self.supplement is not None:
            args.append(f"supplement: {utils.render(self.supplement)}")
        if self.outlined is not None:
            args.append(f"outlined: {utils.render(self.outlined)}")
        if self.bookmarked is not None:
            args.append(f"bookmarked: {utils.render(self.bookmarked)}")

        if self.level is not None and len(args) == 2:
            # remove unnecessary quotes, because Markdown style is not in code mode
            body = args[0].strip('"')
            heading = "=" * self.level + f" {body}"
        else:
            args[0] = args[0].lstrip("#")  # remove hashtag because of code mode
            heading = f"#heading({', '.join(args)})"

        return heading
