"""Logging configuration for extracta."""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from .config import load_config


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    console: bool = True,
    json_format: bool = False,
) -> None:
    """Setup comprehensive logging configuration."""

    # Get configuration
    config = load_config()

    # Base logging configuration
    log_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(funcName)s %(lineno)d %(message)s",
            }
            if json_format
            else {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {},
        "root": {"level": level, "handlers": []},
        "loggers": {
            "extracta": {"level": level, "handlers": [], "propagate": False},
            "extracta.analyzers": {"level": level, "handlers": [], "propagate": False},
            "extracta.lenses": {"level": level, "handlers": [], "propagate": False},
            "extracta.shared": {"level": level, "handlers": [], "propagate": False},
        },
    }

    # Add console handler
    if console:
        log_config["handlers"]["console"] = {
            "class": "logging.StreamHandler",
            "level": level,
            "formatter": "json" if json_format else "standard",
            "stream": "ext://sys.stdout",
        }

        # Add to all loggers
        for logger_name in log_config["loggers"]:
            log_config["loggers"][logger_name]["handlers"].append("console")
        log_config["root"]["handlers"].append("console")

    # Add file handler
    if log_file:
        log_config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": level,
            "formatter": "detailed",
            "filename": str(log_file),
            "maxBytes": 10 * 1024 * 1024,  # 10MB
            "backupCount": 5,
        }

        # Add to all loggers
        for logger_name in log_config["loggers"]:
            log_config["loggers"][logger_name]["handlers"].append("file")
        log_config["root"]["handlers"].append("file")

    # Apply configuration
    logging.config.dictConfig(log_config)

    # Set up uncaught exception handler
    def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions with logging."""
        if issubclass(exc_type, KeyboardInterrupt):
            # Don't log keyboard interrupts
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger = logging.getLogger("extracta")
        logger.critical(
            "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = handle_uncaught_exception


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger for the given name."""
    return logging.getLogger(f"extracta.{name}")


class LoggerMixin:
    """Mixin to add logging capabilities to classes."""

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        if not hasattr(self, "_logger"):
            self._logger = logging.getLogger(
                f"extracta.{self.__class__.__module__}.{self.__class__.__name__}"
            )
        return self._logger

    def log_error(self, message: str, exc: Optional[Exception] = None, **kwargs):
        """Log an error with optional exception info."""
        if exc:
            self.logger.error(message, exc_info=exc, extra=kwargs)
        else:
            self.logger.error(message, extra=kwargs)

    def log_warning(self, message: str, **kwargs):
        """Log a warning."""
        self.logger.warning(message, extra=kwargs)

    def log_info(self, message: str, **kwargs):
        """Log an info message."""
        self.logger.info(message, extra=kwargs)

    def log_debug(self, message: str, **kwargs):
        """Log a debug message."""
        self.logger.debug(message, extra=kwargs)
