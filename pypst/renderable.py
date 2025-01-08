from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


class Renderable(ABC):
    """
    Abstract base class for any renderable object.

    Any Typst document element should inherit/implement this abstract base class.
    """

    @abstractmethod
    def render(self) -> str:
        pass

    @classmethod
    def __subclasshook__(cls, subclass: Any) -> bool:
        if cls is Renderable:
            if any("render" in B.__dict__ for B in subclass.__mro__):
                return True

        return NotImplemented  # type: ignore[no-any-return]


@dataclass
class Plain:
    """
    Plain string content that is rendered as-is.
    """

    value: str

    def render(self) -> str:
        """
        Render the internal string value as-is.

        Returns:
            The internal string value as-is.
        """
        return self.value
