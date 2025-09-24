from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

import pytest

from pypst import Document, Image, utils


def test_empty_mapping():
    obj = dict()
    assert utils.render(obj) == "(:)"


def test_flat_mapping():
    obj = dict(foo='"bar"', quux='"corge"', qux=None, baz=Image("image.png"))
    assert (
        utils.render(obj)
        == '(foo: "bar", quux: "corge", qux: none, baz: image("image.png"))'
    )


def test_nested_mapping():
    obj = dict(foo=dict(bar='"quux"', qux=None, baz=Image("image.png")))
    assert (
        utils.render(obj) == '(foo: (bar: "quux", qux: none, baz: image("image.png")))'
    )


def test_flat_sequence():
    obj = ('"foo"', "bar", 2, Image("image.png"), None)
    assert utils.render(obj) == '("foo", bar, 2, image("image.png"), none)'


def test_nested_seq():
    obj = ('"foo"', "bar", (2, Image("image.png")), None)
    assert utils.render(obj) == '("foo", bar, (2, image("image.png")), none)'


def test_date():
    obj = date(2024, 12, 18)
    assert utils.render(obj) == "#datetime(year: 2024, month: 12, day: 18)"


@pytest.mark.integration
def test_date_compile(test_compile):
    obj = date(2024, 12, 18)
    assert test_compile(obj)


def test_datetime():
    obj = datetime(2024, 12, 18, 15, 34, 12)
    assert (
        utils.render(obj)
        == "#datetime(year: 2024, month: 12, day: 18, hour: 15, minute: 34, second: 12)"
    )


@pytest.mark.integration
def test_datetime_compile(test_compile):
    obj = datetime(2024, 12, 18, 15, 34, 12)
    test_compile(obj)


def test_timedelta():
    obj = timedelta(days=3, seconds=4)
    assert utils.render(obj) == "#duration(seconds: 4, days: 3)"
    obj = timedelta(
        days=3, seconds=4, microseconds=7e5
    )  # millis are not supported in Typst, but we round them to seconds.
    assert utils.render(obj) == "#duration(seconds: 5, days: 3)"


@pytest.mark.integration
def test_timedelta_compile(test_compile):
    obj = timedelta(
        days=3, seconds=4, microseconds=7e5
    )  # millis are not supported in Typst, but we round them to seconds.
    test_compile(obj)


@dataclass
class Foo(utils.Dictionary):
    bar: int = 3
    qux: float | None = 3.14


def test_dataclass():
    assert Foo().render() == "#(bar: 3, qux: 3.14)"
    assert Foo(bar=None, qux=None).render() == "#(:)"
    assert str(Foo()) == Foo().render()
    assert Foo(bar=5, qux=None).render() == "#(bar: 5)"
    assert Foo(bar=5, qux="none").render() == "#(bar: 5, qux: none)"


@pytest.mark.integration
def test_dataclass_compile(test_compile):
    obj = Foo()
    test_compile(obj)


@dataclass
class EmptyFn(utils.Function):
    nope: int | None = None


def test_empty_fn():
    assert (
        EmptyFn().render() == "#empty-fn()"
    ), "ensure that an empty function call is just () and not (:) like a mapping"
    assert EmptyFn(2).render() == "#empty-fn(nope: 2)"


@dataclass
class FooFn(utils.Function):
    __is_function__ = True
    bar: int = field(metadata={"positional": True})
    qux: int = 16
    yes: int | None = field(default=None, metadata={"keep_none": True})
    skip_me: int | None = field(default=None, metadata={"skip": True})
    rename_me: int | None = field(default=1, metadata={"name": "one"})


def test_function():
    obj = FooFn(4, skip_me=2)
    assert obj.render() == "#foo-fn(4, qux: 16, yes: none, one: 1)"
    assert obj.render() == str(obj)


@pytest.mark.integration
def test_function_compile(test_compile):
    @dataclass
    class Rect(utils.Function):
        body: str | None = field(default=None, metadata={"positional": True})
        width: str = "10em"
        height: str = "10%"
        fill: str = "red"

    obj = Rect()
    assert obj.render() == "#rect(width: 10em, height: 10%, fill: red)"
    test_compile(obj)

    obj = Rect('"hello world"')
    assert obj.render() == '#rect("hello world", width: 10em, height: 10%, fill: red)'
    test_compile(obj)


def test_empty_string():
    obj = utils.String()
    assert obj.render() == '#""'


def test_escaped_string():
    line = "The most 'common' string in programming is: " + '"Hello world!".'
    s = utils.String(line)
    assert (
        s.render()
        == '#"The most \'common\' string in programming is: \\"Hello world!\\"."'
    )


def test_char_string():
    s = utils.String("Hëlló wòrld!")
    assert s.render() == '#"Hëlló wòrld!"'


@pytest.mark.integration
def test_escaped_string_compile(test_compile):
    line = "The most 'common' string in programming is: " + '"Hello world!".'
    s = utils.String(line)
    let = f"#let foo = {utils.render_code(s)}"
    check = '#assert.eq(foo, "The most \'common\' string in programming is: \\"Hello world!\\".")'
    doc = Document([let, check])
    test_compile(doc)
