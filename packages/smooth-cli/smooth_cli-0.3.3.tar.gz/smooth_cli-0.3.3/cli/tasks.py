from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # Ruff TCH003: typing-only imports
    from collections.abc import Sequence  # noqa: F401


def test() -> int:
    import pytest

    return int(pytest.main([]))


def test_coverage() -> int:
    import pytest
    from coverage import Coverage

    cov = Coverage(config_file="pyproject.toml")
    cov.start()
    rc = int(pytest.main(["-q"]))
    cov.stop()
    cov.save()
    try:
        cov.report(config_file="pyproject.toml", fail_under=85)
    except Exception:
        # Keep pytest's return code precedence
        if rc == 0:
            return 1
    return rc


def lint() -> int:
    try:
        from ruff.__main__ import main as ruff_main
    except Exception:
        return 1
    return int(ruff_main(["check", "."]))


def format() -> int:  # noqa: A001 - script name
    try:
        from ruff.__main__ import main as ruff_main
    except Exception:
        return 1
    return int(ruff_main(["format", "."]))


def typecheck() -> int:
    try:
        from mypy import api as mypy_api
    except Exception:
        return 1
    _out, _err, status = mypy_api.run(["."])
    return int(status or 0)


def security() -> int:
    try:
        # bandit API; convert SystemExit to int code
        from bandit.__main__ import main as bandit_main
    except Exception:
        return 1
    try:
        bandit_main(["-q", "./*.py"])  # type: ignore[arg-type]
    except SystemExit as e:  # bandit exits with status
        return int(e.code or 0)
    else:
        return 0


def check() -> int:
    for fn in (test, lint, typecheck, security):
        code = fn()
        if code != 0:
            return code
    return 0
