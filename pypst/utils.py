from typing import Sequence, Mapping, Iterable, Any


def render_arg(arg: int | str | Sequence[str] | Mapping[str, str]) -> str:
    if isinstance(arg, int | float):
        rendered_arg = str(arg)
    elif isinstance(arg, str):
        rendered_arg = arg
    elif isinstance(arg, Sequence):
        rendered_arg = render_sequence(arg)
    elif isinstance(arg, Mapping):
        rendered_arg = render_mapping(arg)
    else:
        raise ValueError(f"Invalid argument type: {type(arg)}")

    return rendered_arg


def render_mapping(arg: Mapping[str, str | int | float]) -> str:
    return render_sequence(f"{k}: {v}" for k, v in arg.items())


def render_sequence(arg: Iterable[Any]) -> str:
    return f"({', '.join(a for a in arg)})"
