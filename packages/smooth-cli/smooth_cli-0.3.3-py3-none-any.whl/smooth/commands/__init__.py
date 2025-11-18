from contextlib import suppress

with suppress(Exception):
    from . import auth, docs  # noqa: F401
