from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from pypst.renderable import Renderable
from pypst.utils import render_code


@dataclass
class SetRule:
    """
    Typst set rule.

    Examples:
        >>> rule = SetRule(selector="text", arguments={"fill": "red"})
        >>> rule.render()
        '#set text(fill: red)'

        >>> from pypst import ShowRule
        >>> rule = ShowRule(selector="heading", body=SetRule("text", {"fill": "red"}))
    """

    selector: str | Renderable
    arguments: Mapping[str, Any] | Renderable

    def __str__(self) -> str:
        return self.render()

    def render(self) -> str:
        """
        Render the set rule to a string.
        """
        return f"#set {render_code(self.selector)}{render_code(self.arguments)}"
