from dataclasses import dataclass

from pypst.content import Content
from pypst.functional import Functional
from pypst.renderable import Renderable
from pypst.utils import render_code


@dataclass
class ShowRule:
    """
    Typst show rule.

    Examples:
        >>> rule = ShowRule(selector="heading", body="text.with(fill: red)")
        >>> rule.render()
        '#show heading: text.with(fill: red)'

        >>> rule = ShowRule(selector="heading", argument="it", body="text(fill: red, it)")
        >>> print(rule.render())
        #show heading: it => text(fill: red, it)

        >>> rule = ShowRule(selector="heading", argument="it", body=Functional(["v(0.5em)", "it"]))
        >>> print(rule.render())
        #show heading: it => {
          v(0.5em)
          it
        }

        >>> rule = ShowRule(selector="heading", argument="it", body=Content(["#v(0.5em)", "#it"]))
        >>> print(rule.render())
        #show heading: it => [
          #v(0.5em)
          #it
        ]
    """

    selector: str | Renderable | None = None
    argument: str | Renderable | None = None
    body: str | Renderable | None = None
    indent: int = 2

    def __post_init__(self) -> None:
        if not isinstance(self.body, (Functional, Content)):
            body = Functional(self.body, indent=self.indent)
            assert isinstance(body, Renderable)
            self.body = body

    def __str__(self) -> str:
        return self.render()

    def render(self) -> str:
        """
        Render the show rule to a string.
        """
        target = "" if self.selector is None else f" {self.selector}"

        if self.body is None:
            body = "none"
        else:
            # Render functional or content block.
            body = render_code(self.body)

            # Remove brackets from one-liner functional blocks that don't initiate a context.
            if (
                isinstance(self.body, Functional)
                and not self.body.context
                and "\n" not in body
            ):
                body = body[1:-1]

        if self.argument is None:
            return f"#show{target}: {body}"
        else:
            argument = render_code(self.argument)
            return f"#show{target}: {argument} => {body}"
