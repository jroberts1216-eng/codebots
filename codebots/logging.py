from __future__ import annotations

import logging
from dataclasses import dataclass
from rich.console import Console
from rich.logging import RichHandler

_console = Console()


@dataclass(frozen=True)
class LogConfig:
    level: int = logging.INFO


def setup_logging(cfg: LogConfig | None = None) -> None:
    cfg = cfg or LogConfig()
    logging.basicConfig(
        level=cfg.level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=_console, rich_tracebacks=True)],
    )
