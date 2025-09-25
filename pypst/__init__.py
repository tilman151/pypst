from typing import Any

from pypst.cell import Cell
from pypst.content import Content
from pypst.document import Document
from pypst.figure import Figure
from pypst.functional import Functional
from pypst.heading import Heading
from pypst.image import Image
from pypst.itemize import Enumerate, Itemize
from pypst.renderable import Plain, Renderable
from pypst.set_rule import SetRule
from pypst.show_rule import ShowRule

try:
    from pypst.table import Table  # needed to be included in code completion
except ModuleNotFoundError:
    pass


def __getattr__(name: str) -> Any:
    """Lazily import Table to check for pandas."""
    if name == "Table":
        from pypst.table import Table

        return Table
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "Cell",
    "Content",
    "Document",
    "Enumerate",
    "Figure",
    "Functional",
    "Heading",
    "Image",
    "Itemize",
    "Plain",
    "Renderable",
    "SetRule",
    "ShowRule",
    "Table",
]
__version__ = "0.7.0"
