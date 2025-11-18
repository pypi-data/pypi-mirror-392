import logging
import warnings
from pathlib import Path
from typing import Union

try:
    import colorlog
except ImportError:
    colorlog = None


class Logger:
    """
    Упрощённая обёртка над logging.

    Особенности:
    - не дублирует хендлеры при повторном создании с тем же name;
    - может логировать в консоль (c цветом, если есть colorlog) и/или в файл;
    - безопасен к многократному использованию в одном процессе.
    """

    def __init__(
        self,
        name: str = "asfeslib",
        log_to_file: bool = False,
        log_file: Union[str, Path] = "asfeslib.log",
        level: int = logging.DEBUG,
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False

        if not any(isinstance(h, logging.StreamHandler) for h in self.logger.handlers):
            console_handler = self._build_console_handler(level)
            self.logger.addHandler(console_handler)

        self.log_to_file = log_to_file
        self.log_file = Path(log_file)

        if self.log_to_file:
            self._log_to_file(level)

    def enable_file_logging_legacy(self, level: int = logging.DEBUG) -> None:
        """
        УСТАРЕВШИЙ МЕТОД.
        Используйте параметр log_to_file=True в __init__ или метод enable_file_logging().
        """

        warnings.warn(
            "enable_file_logging_legacy() is deprecated, use enable_file_logging() instead.",
            category=DeprecationWarning,
            stacklevel=2,
        )

        self.enable_file_logging(level)
        
    def enable_file_logging(self, level: int = logging.DEBUG) -> None:
        """Современный способ включить логирование в файл."""
        self.log_to_file = True
        self._log_to_file(level)

    def _build_console_handler(self, level: int) -> logging.Handler:
        handler = logging.StreamHandler()
        handler.setLevel(level)

        if colorlog is not None:
            log_format = "%(log_color)s[%(asctime)s] [%(levelname)s]%(reset)s %(message)s"
            formatter = colorlog.ColoredFormatter(
                log_format,
                datefmt="%Y-%m-%d %H:%M:%S",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "bold_red",
                },
            )
        else:
            formatter = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] %(message)s",
                "%Y-%m-%d %H:%M:%S",
            )

        handler.setFormatter(formatter)
        return handler

    def _log_to_file(self, level: int) -> None:
        for h in self.logger.handlers:
            if isinstance(h, logging.FileHandler) and getattr(h, "_asfes_log_file", None) == str(self.log_file):
                return

        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
        file_handler._asfes_log_file = str(self.log_file)
        file_handler.setLevel(level)

        file_format = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)

    def debug(self, msg: str, *args, **kwargs) -> None:
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs) -> None:
        self.logger.exception(msg, *args, **kwargs)
