from collections.abc import Iterable
from dataclasses import dataclass

from pypst.renderable import Renderable
from pypst.utils import render, render_fenced


@dataclass
class Content:
    """
    Typst content block explicitly wrapped in [].

    Example:
        >>> content = Content("Foo is a bar.")
        >>> content.render()
        '#[Foo is a bar.]'

        >>> from pypst import SetRule
        >>> content = Content([SetRule("text", {"fill": "red"}), "This text will be red."])
        >>> print(content.render())
        #[
          #set text(fill: red)
          This text will be red.
        ]

        >>> from pypst import SetRule
        >>> content = Content([SetRule("text", {"fill": "red"}), "This is page #here().page()"], context=True)
        >>> print(content.render())
        #context [
          #set text(fill: red)
          This is page #here().page()
        ]
    """

    body: str | Renderable | Iterable[str | Renderable] | None = None
    context: bool = False
    joint: str = "\n"
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
        return render_fenced(
            body=self.body,
            context=self.context,
            joint=self.joint,
            indent=self.indent,
            start="[",
            end="]",
            render_fn=render,
        )
