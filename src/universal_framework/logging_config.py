"""Centralized logging setup."""

from __future__ import annotations

import logging


_HANDLER_MARKER = "_universal_framework_console_handler"


def configure_logging(level: str = "INFO", logger_name: str = "universal_framework") -> logging.Logger:
    """Return a configured console logger without adding duplicate handlers."""
    normalized = level.upper()
    numeric_level = logging.getLevelName(normalized)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Unsupported log level: {level}")

    logger = logging.getLogger(logger_name)
    logger.setLevel(numeric_level)
    logger.propagate = False

    if not any(getattr(handler, _HANDLER_MARKER, False) for handler in logger.handlers):
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        setattr(handler, _HANDLER_MARKER, True)
        logger.addHandler(handler)

    return logger
