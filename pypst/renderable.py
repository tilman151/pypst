from abc import ABC, abstractmethod
from typing import Any


class Renderable(ABC):
    @abstractmethod
    def render(self) -> str:
        pass

    @classmethod
    def __subclasshook__(cls, subclass: Any) -> bool:
        if cls is Renderable:
            if any("render" in B.__dict__ for B in subclass.__mro__):
                return True

        return NotImplemented
