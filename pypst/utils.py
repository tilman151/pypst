import json
import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import Field, dataclass, fields, is_dataclass
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
    elif is_dataclass(arg):
        rendered_arg = render_dataclass(arg)
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


def render_dataclass(arg: Any) -> str:
    """
    Render a dataclass as either a mapping or a function call.

    The existence and value of an `__is_function__` member on the object
    determines whether it is rendered as a function call. Setting it to return

    Rendering of positional arguments in a Typst function call can be accomplished
    by setting the `positional=True` flag on the dataclass field's metadata.

    You can specify that `None` values should be rendered instead
    of being skipped with `keep_none=True` on the dataclass field's metadata.

    Examples:
        >>> from dataclasses import dataclass, field
        >>> @dataclass
        ... class Foo:
        ...    bar: int | None = 4
        ...    qux: int | None = field(default=16, metadata={"keep_none": True})
        >>>
        >>> render(Foo())
        '#(bar: 4, qux: 16)'
        >>> render(Foo(bar=None))
        '#(qux: 16)'
        >>> render(Foo(qux=None))
        '#(bar: 4, qux: none)'

        >>> @dataclass
        ... class FooFn:
        ...    __is_function__ = True
        ...    bar: int | None = field(metadata={"positional": True})
        ...    qux: int | None = field(default=16, metadata={"keep_none": True})
        >>>
        >>> render(FooFn(4))
        '#foo-fn(4, qux: 16)'
        >>> render(FooFn(None))
        '#foo-fn(qux: 16)'
        >>> render(FooFn(4, qux=None))
        '#foo-fn(4, qux: none)'
    """

    function = getattr(arg, "__is_function__", False)
    fields = dataclass_fields_to_render(arg)

    if function:
        function = (
            function
            if isinstance(function, str)
            else camel_to_kebab_case(arg.__class__.__name__)
        )

        arguments = ", ".join(
            render_code(getattr(arg, field.name))
            if field.metadata.get("positional", False)
            else f"{field.name}: {render_code(getattr(arg, field.name))}"
            for field in fields
        )

        rendered = f"#{function}({arguments})"
    else:
        mapping = render_mapping(
            {field.name: getattr(arg, field.name) for field in fields}
        )
        rendered = f"#{mapping}"

    return rendered


def dataclass_fields_to_render(arg: Any) -> Iterable[Field]:
    """
    These dataclass fields should be rendered.
    Defaults to skipping any fields with a value of `None`.
    """

    def check(field: Field) -> bool:
        # When the value is `None`, check whether that should be kept.
        if getattr(arg, field.name) is None:
            return field.metadata.get("keep_none", False)

        # Keep otherwise.
        return True

    return filter(check, fields(arg))


def camel_to_kebab_case(arg: str) -> str:
    """
    Transform a CamelCase string to kebab-case.

    Examples:
        >>> camel_to_kebab_case("ClassName")
        'class-name'
    """
    return re.sub(
        r"([a-z0-9])([A-Z])",
        r"\1-\2",
        arg,
    ).lower()


def render_fenced(
    body: str | Renderable | Iterable[str | Renderable] | None = None,
    context: bool = False,
    start: str = "{",
    end: str = "}",
    indent: int = 2,
    joint: str = "\n",
    render_fn: Callable[[Any], str] = render_code,
) -> str:
    """
    Render a Typst fenced code block such as #{} and #[].

    Example:
        >>> render_fenced()
        '#{}'

        >>> from pypst import Content, SetRule
        >>> string = render_fenced([SetRule("text", {"fill": "red"}), Content("This text will be red.")])
        >>> print(string)
        #{
          set text(fill: red)
          [This text will be red.]
        }
    """

    ctx = "context " if context else ""

    if isinstance(body, (str, Renderable)):
        body = render_fn(body)
    elif isinstance(body, Iterable):
        body = joint.join(render_fn(entry) for entry in body)
    elif body is None:
        body = ""
    else:
        body = render_fn(body)

    if indent is None:
        return f"#{ctx}{start}{body}{end}"

    if "\n" in body:
        newline = f"\n{indent * ' '}"
        indented = body.replace("\n", newline)
        return f"#{ctx}{start}{newline}{indented}\n{end}"

    return f"#{ctx}{start}{body}{end}"


class _RenderDataclass:
    """
    Helper class that implements default dataclass rendering for dictionaries and functions.
    """

    def __str__(self) -> str:
        return self.render()

    def render(self) -> str:
        """
        Render this dataclass as a string. See `render_dataclass` for more information.
        """
        return render_dataclass(self)


class Dictionary(_RenderDataclass):
    """
    Helper class that implements default dataclass rendering for dictionaries in Typst.

    Examples:
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


class Function(_RenderDataclass):
    """
    Helper class that implements default dataclass rendering for function calls in Typst.

    By default, the class name is converted to kebab-case as the function name.
    You can override this behavior by setting the `__is_function__` class variable
    to a string of your choice.

    Examples:
        >>> from dataclasses import dataclass, field
        >>> @dataclass
        ... class FooFn(Function):
        ...    __is_function__ = True
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

    __is_function__: bool | str = True


@dataclass
class String:
    """
    String helper that wraps any content in quotes.

    Example:
        >>> line = (
        ...     "The most 'common' string in programming is: "
        ...     '"Hello world!".'
        ... )
        >>> s = String(line)
        >>> print(s.render())
        #"The most 'common' string in programming is: \\"Hello world!\\"."
    """

    body: str | Renderable | None = None

    def __post_init__(self) -> None:
        if isinstance(self.body, String):
            self.body = self.body.body

    def render(self) -> str:
        """
        Render the internal body to a string, escaping any symbols in JSON fashion.
        """
        body = json.dumps(
            "" if self.body is None else render_code(self.body), ensure_ascii=False
        )
        # Always assume we're in content mode.
        return f"#{body}"
