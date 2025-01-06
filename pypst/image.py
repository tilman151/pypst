from dataclasses import dataclass, field
from typing import Literal

from pypst.utils import Function


@dataclass
class Image(Function):
    """
    Image object to add image elements.

    The image file needs to be in the provided path.
    The path is interpreted as relative to the Typst file.

    Args:
        path: Path to the image file.
        format: The image format.
        width: The width the image should occupy.
        height: The height the image should occupy.
        alt: The image alt text.
        fit: How the image fills the space defined by `width` and `height`.

    Examples:
        >>> image = Image(path="image.png", width="100%", height="50%")
        >>> print(image.render())
        #image("image.png", width: 100%, height: 50%)
    """

    __is_function__ = True

    path: str = field(metadata={"positional": True})
    format: Literal["png", "jpg", "gif", "svg"] | str | None = None
    width: str | None = None
    height: str | None = None
    alt: str | None = None
    fit: Literal["cover", "contain", "stretch"] | str | None = None

    def __post_init__(self) -> None:
        if not self.path.startswith('"'):
            self.path = f'"{self.path}"'

        if self.format is not None and not self.format.startswith('"'):
            self.format = f'"{self.format}"'

        if self.fit is not None and not self.fit.startswith('"'):
            self.fit = f'"{self.fit}"'
