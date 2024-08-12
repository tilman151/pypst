from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Document:
    body: Any

    imports: list["Import"] = field(default_factory=list)

    def add_import(self, module: str, members: Optional[list[str]] = None) -> None:
        self.imports.append(Import(module, members or []))

    def render(self) -> str:
        imports = "\n".join([i.render() for i in self.imports])
        body: str = self.body.render()

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
