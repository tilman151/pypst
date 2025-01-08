import builtins
import sys

import pytest


@pytest.fixture
def missing_pandas(monkeypatch):
    real_import = builtins.__import__

    def _import_error(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "pandas":
            raise ImportError(f"Mocked import error {name}")
        return real_import(
            name, globals=globals, locals=locals, fromlist=fromlist, level=level
        )

    monkeypatch.setattr(builtins, "__import__", _import_error)
    monkeypatch.delitem(sys.modules, "pandas")


def test_error_on_importing_table_without_pandas(monkeypatch, missing_pandas):
    monkeypatch.delitem(sys.modules, "pypst.table")
    with pytest.raises(ModuleNotFoundError):
        import pypst.table  # noqa: F401


def test_error_on_using_Table_without_pandas(monkeypatch, missing_pandas):
    monkeypatch.delitem(sys.modules, "pypst")
    monkeypatch.delitem(sys.modules, "pypst.table")

    import pypst

    with pytest.raises(ModuleNotFoundError):
        pypst.Table()
