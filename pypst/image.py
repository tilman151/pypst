from dataclasses import dataclass
from typing import Optional, Literal


@dataclass
class Image:
    path: str
    format: Optional[Literal["png", "jpg", "gif", "svg"]] = None
    width: Optional[str] = None
    height: Optional[str] = None
    alt: Optional[str] = None
    fit: Optional[Literal["cover", "contain", "stretch"]] = None

    def render(self) -> str:
        path = self.path if self.path.startswith('"') else f'"{self.path}"'
        args = [path]
        if self.format is not None:
            args.append(f'format: "{self.format}"')
        if self.width is not None:
            args.append(f"width: {self.width}")
        if self.height is not None:
            args.append(f"height: {self.height}")
        if self.alt is not None:
            args.append(f"alt: {self.alt}")
        if self.fit is not None:
            args.append(f'fit: "{self.fit}"')
        rendered = f"#image({', '.join(args)})"

        return rendered
