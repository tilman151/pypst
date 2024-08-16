from dataclasses import dataclass
from typing import Optional, Literal


@dataclass
class Image:
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

    path: str
    format: Optional[Literal["png", "jpg", "gif", "svg"]] = None
    width: Optional[str] = None
    height: Optional[str] = None
    alt: Optional[str] = None
    fit: Optional[Literal["cover", "contain", "stretch"]] = None

    def render(self) -> str:
        """
        Render the image element to a string.

        Returns:
            The rendered image element.
        """
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
