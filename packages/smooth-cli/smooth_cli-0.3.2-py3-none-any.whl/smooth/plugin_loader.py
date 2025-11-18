import logging
import typing
from importlib import metadata

import typer


def load_plugins(app: typer.Typer) -> None:
    try:
        eps = metadata.entry_points().select(group="smooth.plugins")
    except Exception as err:
        logging.debug("plugin discovery failed: %s", err)
        return
    for ep in eps:
        try:
            register: typing.Callable[[typer.Typer], None] = ep.load()
            register(app)
        except Exception as err:
            logging.debug("plugin load failed for %s: %s", getattr(ep, "name", "<unknown>"), err)
            continue
