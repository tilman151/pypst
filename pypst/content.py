from dataclasses import dataclass

from pypst.renderable import Renderable
from pypst.utils import render


@dataclass
class Content:
    """
    Typst content block explicitly wrapped in [].

    Example:
        >>> content = Content("Foo is a bar.")
        >>> content.render()
        '#[Foo is a bar.]'

        >>> from pypst import Set
        >>> content = Content([Set("text", {"fill": "red"}), "This text will be red."])
        >>> print(content.render())
        #[
          #set text(fill: red)
          This text will be red.
        ]

        >>> from pypst import Set
        >>> content = Content([Set("text", {"fill": "red"}), "This is page #here().page()"], context=True)
        >>> print(content.render())
        #context [
          #set text(fill: red)
          This is page #here().page()
        ]
    """

    body: str | Renderable | list[str | Renderable] | None = None
    context: bool = False
    indent: int = 2

    def __post_init__(self) -> None:
        if isinstance(self.body, Content):
            self.context = self.context or self.body.context
            self.body = self.body.body

    def __str__(self) -> str:
        return self.render()

    def render(self) -> str:
        """
        Render the content block to a string.
        """
        context = "context " if self.context else ""

        if isinstance(self.body, list):
            body = "\n".join(render(entry) for entry in self.body)
        elif self.body is None:
            body = ""
        else:
            body = render(self.body)

        if self.indent is None:
            return f"#{context}[{body}]"

        lines = body.splitlines()
        if len(lines) > 1:
            indent = self.indent * " "
            indented = f"{indent}\n".join(lines)
            return f"#{context}[\n{indent}{indented}\n]"

        return f"#{context}[{body}]"
