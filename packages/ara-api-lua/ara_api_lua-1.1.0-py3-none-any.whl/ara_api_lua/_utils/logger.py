import inspect
import logging
import os
import sys
from datetime import datetime
from typing import Literal, Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme


class Logger:
    """
    Flexible logger that can write to file, terminal, or both.
    Can automatically detect the calling class name.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        log_level: str = "INFO",
        log_to_file: bool = True,
        log_to_terminal: bool = True,
        log_dir: str = "logs",
        use_rich: bool = True,
    ) -> None:
        if name is None:
            frame = inspect.currentframe().f_back
            if frame:
                try:
                    calling_class = frame.f_locals.get("self", None).__class__.__name__
                    name = calling_class
                except (AttributeError, KeyError):
                    name = frame.f_globals.get("__name__", "unknown")

        self.name = name
        self.log_level = getattr(logging, log_level)
        self.log_to_file = log_to_file
        self.log_to_terminal = log_to_terminal
        self.log_dir = log_dir
        self.use_rich = use_rich

        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)
        self.logger.handlers = []

        # Create formatters
        self.file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.terminal_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        )

        self.console = Console(
            theme=Theme(
                {
                    "debug": "dim white",
                    "info": "cyan",
                    "warning": "yellow",
                    "error": "bold red",
                    "critical": "bold white on red",
                }
            ),
        )

        if self.log_to_file:
            self._setup_file_handler()

        if self.log_to_terminal:
            self._setup_terminal_handler()

    def _setup_file_handler(self) -> None:
        os.makedirs(self.log_dir, exist_ok=True)

        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = f"{self.log_dir}/{date_str}_{self.name}.log"

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(self.file_formatter)
        self.logger.addHandler(file_handler)

    def _setup_terminal_handler(self) -> None:
        if self.use_rich:
            rich_handler = RichHandler(
                console=self.console,
                show_time=True,
                show_level=True,
                show_path=False,
                rich_tracebacks=True,
                tracebacks_show_locals=True,
                log_time_format="[%H:%M:%S]",
            )
            rich_handler.setLevel(self.log_level)
            self.logger.addHandler(rich_handler)
        else:
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setLevel(self.log_level)
            stream_handler.setFormatter(self.terminal_formatter)
            self.logger.addHandler(stream_handler)

    def reconfigure(
        self,
        log_level: Optional[str] = None,
        log_to_file: Optional[bool] = None,
        log_to_terminal: Optional[bool] = None,
    ) -> None:
        changed = False

        if log_level is not None and log_level != self.log_level:
            self.log_level = getattr(logging, log_level)
            changed = True

        if log_to_file is not None and log_to_file != self.log_to_file:
            self.log_to_file = log_to_file
            changed = True

        if log_to_terminal is not None and log_to_terminal != self.log_to_terminal:
            self.log_to_terminal = log_to_terminal
            changed = True

        if changed:
            self.logger.handlers = []

            if self.log_to_file:
                self._setup_file_handler()

            if self.log_to_terminal:
                self._setup_terminal_handler()

            self.logger.setLevel(self.log_level)
            for handler in self.logger.handlers:
                handler.setLevel(self.log_level)

    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)

    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)

    def critical(self, message: str) -> None:
        """Log critical message."""
        self.logger.critical(message)
