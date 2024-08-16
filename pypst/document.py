from dataclasses import dataclass, field
from typing import Optional

from pypst import utils
from pypst.renderable import Renderable


class Document:
    """
    Represents a Typst document serving as the top-level container.

    A document contains other renderable objects and necessary imports.
    It is only necessary if multiple renderable objects need to be combined
    or third-party files need to be imported.

    Examples:
            >>> doc = Document("Hello, world!")
            >>> print(doc.render())
            Hello, world!

            >>> doc = Document(["Hello,", "world!"])
            >>> print(doc.render())
            Hello,
            <BLANKLINE>
            world!

            >>> doc = Document()
            >>> doc.add("Hello,")
            >>> doc.add("world!")
            >>> print(doc.render())
            Hello,
            <BLANKLINE>
            world!

            >>> doc = Document()
            >>> doc.add_import("module")
            >>> doc.add("Hello, world!")
            >>> print(doc.render())
            #import "module"
            <BLANKLINE>
            Hello, world!
    """

    _body: list[Renderable | str]
    imports: list["Import"]

    def __init__(
        self, body: Optional[Renderable | str | list[Renderable | str]] = None
    ) -> None:
        """
        Create a new document with an optional body.

        The body can be a single renderable object, a string,
        or a list of renderable objects and strings.

        Args:
            body: The body of the document.
        """
        self._body = []
        self.imports = []

        if body is None:
            body = []
        elif not isinstance(body, list):
            body = [body]
        for b in body:
            self.add(b)

    @property
    def body(self) -> list[Renderable | str]:
        """The body of the document."""
        return self._body

    def add(self, element: Renderable | str) -> None:
        """
        Add a body element to the document.

        Any object of the `pypst` library with a `render` method can be added.
        Simple text paragraphs or unsupported Typst elements can be added as
        strings.
        Adding an `Import` object is equivalent to calling `add_import`.

        Args:
            element: The new body element.
        """
        if not isinstance(element, (Renderable, str)):
            raise ValueError(f"Invalid body type: {type(element)}")
        elif isinstance(element, Document):
            raise ValueError("Document cannot be set as value of another document")
        elif isinstance(element, Import):
            self.imports.append(element)
        else:
            self._body.append(element)

    def add_import(self, module: str, members: Optional[list[str]] = None) -> None:
        """
        Add an import to the document.

        If members are provided,
        only those members will be imported as `#import <module>: <list of members>`.
        If no members are provided, the entire module will be imported as
        `#import <module>`.
        Imports are rendered at the top of the document.

        Args:
            module: The module to import.
            members: The optional list of members to import.
        """
        self.imports.append(Import(module, members or []))

    def render(self) -> str:
        """
        Render the document.

        The rendered document has all imports at the top followed by the body.
        Each element in the body is rendered in the order it was added.
        A blank line separates each body element.

        Returns:
            The rendered document string.
        """
        imports = "\n".join([i.render() for i in self.imports])
        body = "\n\n".join(utils.render(b) for b in self.body)

        if imports:
            return f"{imports}\n\n{body}"
        else:
            return body


@dataclass
class Import:
    module: str
    members: list[str] = field(default_factory=list)

    def render(self) -> str:
        module = self.module.strip('"')
        module = f'"{module}"'
        rendered_import = f"#import {module}"
        if self.members:
            if "*" in self.members and len(self.members) > 1:
                raise ValueError(
                    f"Error while rendering import for '{self.module}'. "
                    "Cannot import all and specific members at the same time"
                )
            members = ", ".join(self.members)
            rendered_import += f": {members}"

        return rendered_import
