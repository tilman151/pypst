from typing import Any

try:
    from pypst.table import Table  # needed to be included in code completion
except ModuleNotFoundError:
    pass
from pypst.cell import Cell
from pypst.figure import Figure
from pypst.document import Document
from pypst.heading import Heading
from pypst.itemize import Itemize, Enumerate
from pypst.image import Image
from pypst.renderable import Renderable, Plain


def __getattr__(name: str) -> Any:
    """Lazily import Table to check for pandas."""
    if name == "Table":
        from pypst.table import Table

        return Table
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "Table",
    "Cell",
    "Figure",
    "Document",
    "Heading",
    "Itemize",
    "Enumerate",
    "Image",
    "Renderable",
    "Plain",
]
__version__ = "0.5.0"
