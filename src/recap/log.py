"""Logging: one file per stage in <meeting>/logs/, plus console output."""

from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


class _ConsoleFormatter(logging.Formatter):
    """Short console lines; tracebacks only when verbose (they always go to the stage log)."""

    def __init__(self, verbose: bool):
        super().__init__("%(levelname)s %(message)s")
        self.verbose = verbose

    def format(self, record: logging.LogRecord) -> str:
        if self.verbose:
            return super().format(record)
        record = logging.makeLogRecord(record.__dict__)
        record.exc_info = record.exc_text = None
        return super().format(record)


def setup_console(verbose: bool = False) -> None:
    root = logging.getLogger("recap")
    for h in [h for h in root.handlers if getattr(h, "_recap_console", False)]:
        root.removeHandler(h)
    handler = logging.StreamHandler()
    handler.setFormatter(_ConsoleFormatter(verbose))
    handler._recap_console = True  # type: ignore[attr-defined]
    root.addHandler(handler)
    root.setLevel(logging.DEBUG if verbose else logging.INFO)


@contextmanager
def stage_log(meeting_dir: Path, stage: str) -> Iterator[logging.Logger]:
    """Yield a logger for `stage` that also writes to <meeting>/logs/<stage>.log (appending)."""
    logs = meeting_dir / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(f"recap.stage.{stage}")
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(logs / f"{stage}.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter(_FORMAT))
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    try:
        yield logger
    finally:
        logger.removeHandler(handler)
        handler.close()
