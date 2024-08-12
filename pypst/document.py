from dataclasses import dataclass, field
from typing import Optional

from pypst import utils
from pypst.renderable import Renderable


@dataclass
class Document:
    body: Renderable | str
    imports: list["Import"] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.body, (Renderable, str)):
            raise ValueError(f"Invalid body type: {type(self.body)}")
        elif isinstance(self.body, Document):
            raise ValueError("Document cannot be set as body of another document")

    def add_import(self, module: str, members: Optional[list[str]] = None) -> None:
        self.imports.append(Import(module, members or []))

    def render(self) -> str:
        imports = "\n".join([i.render() for i in self.imports])
        body: str = utils.render(self.body)

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
