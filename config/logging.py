import logging
import os
from datetime import datetime
from pathlib import Path
import threading

BASE_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = BASE_DIR / "logs"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_lock = threading.Lock()
_configured_loggers: set[str] = set()


def _get_log_level() -> int:
    """Reads LOG_LEVEL from environment, defaults to INFO."""
    level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_str, None)
    if not isinstance(level, int):
        logging.warning("Invalid LOG_LEVEL '%s', falling back to INFO.", level_str)
        return logging.INFO
    return level


def _build_formatter() -> logging.Formatter:
    return logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)


def _build_file_handler(log_level: int) -> logging.FileHandler:
    """Creates a date-stamped file handler, creating the log directory if needed."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"log_{datetime.now().strftime('%Y-%m-%d')}.log"
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setFormatter(_build_formatter())
    handler.setLevel(log_level)
    return handler


def _build_console_handler(log_level: int) -> logging.StreamHandler:
    handler = logging.StreamHandler()
    handler.setFormatter(_build_formatter())
    handler.setLevel(log_level)
    return handler


def get_logger(name: str) -> logging.Logger:
    """
    Returns a named logger with both file and console handlers.

    Handlers are attached only once per logger name — safe to call
    multiple times across modules without duplicating output.

    Args:
        name: Logger name, typically __name__ of the calling module.

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    with _lock:
        if name in _configured_loggers:
            return logger

        log_level = _get_log_level()
        logger.setLevel(log_level)

        # Prevent log records bubbling up to the root logger
        logger.propagate = False

        logger.addHandler(_build_file_handler(log_level))
        logger.addHandler(_build_console_handler(log_level))

        _configured_loggers.add(name)
    return logger
