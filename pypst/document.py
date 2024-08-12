from dataclasses import dataclass, field
from typing import Optional

from pypst import utils
from pypst.renderable import Renderable


class Document:
    _body: list[Renderable | str]
    imports: list["Import"]

    def __init__(self, body: Renderable | str | list[Renderable | str]) -> None:
        self._body = []
        self.imports = []

        if not isinstance(body, list):
            body = [body]
        for b in body:
            self.add(b)

    @property
    def body(self) -> list[Renderable | str]:
        return self._body

    def add(self, body: Renderable | str) -> None:
        if not isinstance(body, (Renderable, str)):
            raise ValueError(f"Invalid body type: {type(body)}")
        elif isinstance(body, Document):
            raise ValueError("Document cannot be set as value of another document")
        elif isinstance(body, Import):
            self.imports.append(body)
        else:
            self._body.append(body)

    def add_import(self, module: str, members: Optional[list[str]] = None) -> None:
        self.imports.append(Import(module, members or []))

    def render(self) -> str:
        imports = "\n".join([i.render() for i in self.imports])
        body = "\n".join(utils.render(b) for b in self.body)

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
