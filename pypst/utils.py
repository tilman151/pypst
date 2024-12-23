import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import Field, dataclass, fields
from datetime import date, datetime, timedelta
from typing import Any

from pypst.renderable import Renderable


def render(
    obj: Renderable
    | bool
    | int
    | float
    | str
    | Sequence[Any]
    | Mapping[str, Any]
    | date
    | datetime
    | timedelta
    | None,
) -> str:
    """
    Render renderable objects using their `render` method
    or use the `render_type` utility to render built-in Python types.
    """
    if isinstance(obj, Renderable):
        rendered = obj.render()
    else:
        rendered = render_type(obj)

    return rendered


def render_code(
    obj: Renderable
    | bool
    | int
    | float
    | str
    | Sequence[Any]
    | Mapping[str, Any]
    | date
    | datetime
    | timedelta
    | None,
) -> str:
    """
    Render renderable objects using the `render` method
    and strip any `#` code-mode prefixes.
    """
    return render(obj).lstrip("#")


def render_type(
    arg: bool
    | int
    | float
    | str
    | Sequence[Any]
    | Mapping[str, Any]
    | date
    | datetime
    | timedelta
    | None,
) -> str:
    """
    Render different built-in Python types.
    """
    if arg is None:
        rendered_arg = "none"
    elif isinstance(arg, bool):
        rendered_arg = str(arg).lower()
    elif isinstance(arg, int | float):
        rendered_arg = str(arg)
    elif isinstance(arg, str):
        rendered_arg = arg
    elif isinstance(arg, Sequence):
        rendered_arg = render_sequence(arg)
    elif isinstance(arg, Mapping):
        rendered_arg = render_mapping(arg)
    elif isinstance(arg, date):
        rendered_arg = render_datetime(arg)
    elif isinstance(arg, timedelta):
        rendered_arg = render_timedelta(arg)
    else:
        raise ValueError(f"Invalid argument type: {type(arg)}")

    return rendered_arg


def render_mapping(arg: Mapping[str, Any]) -> str:
    """
    Render a mapping from string to any object supported by `render`.
    """
    return render_sequence(f"{k}: {render_code(v)}" for (k, v) in arg.items())


def render_sequence(arg: Iterable[Any]) -> str:
    """
    Render a sequence of any object supported by `render`.
    """
    return f"({', '.join(render_code(a) for a in arg)})"


def render_datetime(arg: date | datetime) -> str:
    """
    Render a Python `datetime.date` into a call to the Typst datetime function.
    """
    obj = {
        name: getattr(arg, name)
        for name in ["year", "month", "day", "hour", "minute", "second"]
        if hasattr(arg, name)
    }
    return f"#datetime{render_mapping(obj)}"


def render_timedelta(arg: timedelta) -> str:
    """
    Render a Python `datetime.timedelta` into a call to the Typst duration function.
    """
    obj = {
        name: getattr(arg, name)
        for name in [
            "microseconds",
            "seconds",
            "days",
        ]
        if hasattr(arg, name)
    }
    obj["seconds"] = obj["seconds"] + round(obj.pop("microseconds") / 1e6)
    return f"#duration{render_mapping(obj)}"


@dataclass
class Dictionary:
    """
    Helper class to render Python dataclasses by iterating over its fields
    as if it were a dictionary.

    Inherit from `Dictionary` to inherit the render method
    and use it with your dataclass.

    You can specify that `None` values should be rendered instead
    of being skipped with `keep_none=True` on the field's metadata.

    Example:
        >>> from dataclasses import dataclass, field
        >>> @dataclass
        ... class Foo(Dictionary):
        ...    bar: int | None = 4
        ...    qux: int | None = field(default=16, metadata={"keep_none": True})
        >>>
        >>> Foo().render()
        '#(bar: 4, qux: 16)'
        >>> Foo(bar=None).render()
        '#(qux: 16)'
        >>> Foo(qux=None).render()
        '#(bar: 4, qux: none)'
    """

    def __str__(self) -> str:
        return self.render()

    def render(self) -> str:
        """
        Dataclass rendering to a Typst dictionary.

        Modify `fields_to_render` to control which fields are included.
        """
        mapping = render_mapping(
            {field.name: getattr(self, field.name) for field in self.fields_to_render()}
        )
        return f"#{mapping}"

    def fields_to_render(self) -> Iterable[Field]:
        """
        These fields should be rendered. Defaults to skipping any fields with a value of `None`.
        """

        def check(field: Field) -> bool:
            # When the value is `None`, check whether that should be kept.
            if getattr(self, field.name) is None:
                return field.metadata.get("keep_none", False)

            # Keep otherwise.
            return True

        return filter(check, fields(self))


@dataclass
class Function(Dictionary):
    """
    Helper class to render Typst function calls from a Python dataclass.

    Inherit from `Function` to inherit the render method.
    The function name is derived from the class name
    and is converted to kebab-case.

    The dataclass' fields are used as the function arguments.

    You can specify a positional argument in Typst by adding
    `positional=True` on the field's metadata.

    You can specify that `None` values should be rendered instead
    of being skipped with `keep_none=True` on the field's metadata.

    Example:
        >>> from dataclasses import dataclass, field
        >>> @dataclass
        ... class FooFn(Function):
        ...    bar: int | None = field(metadata={"positional": True})
        ...    qux: int | None = field(default=16, metadata={"keep_none": True})
        >>>
        >>> FooFn(4).render()
        '#foo-fn(4, qux: 16)'
        >>> FooFn(None).render()
        '#foo-fn(qux: 16)'
        >>> FooFn(4, qux=None).render()
        '#foo-fn(4, qux: none)'
    """

    def render(self) -> str:
        """
        Dataclass rendering to a Typst function call.

        Modify `fields_to_render` to control which fields are included.
        """

        function = self.function()

        options = ", ".join(
            render_code(getattr(self, field.name))
            if field.metadata.get("positional", False)
            else f"{field.name}: {render_code(getattr(self, field.name))}"
            for field in self.fields_to_render()
        )

        return f"#{function}({options})"

    @classmethod
    def function(cls) -> str:
        """
        Class method that returns the Typst function name that it represents.

        Defaults to a kebab-case transformation of the ClassName.
        """
        return re.sub(
            r"([a-z0-9])([A-Z])",
            r"\1-\2",
            cls.__name__,
        ).lower()
