from abc import ABC, abstractmethod


class Renderable(ABC):
    @abstractmethod
    def render(self):
        pass

    @classmethod
    def __subclasshook__(cls, subclass):
        if cls is Renderable:
            if any("render" in B.__dict__ for B in subclass.__mro__):
                return True
        return NotImplemented
