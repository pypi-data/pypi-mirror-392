import logging
import sys
from types import FrameType
from typing import Optional

import openai
from loguru import logger

openai._utils._logs.logger.setLevel(logging.WARNING)
openai._utils._logs.httpx_logger.setLevel(logging.WARNING)


class InterceptHandler(logging.Handler):
    """Redirect standard logging records to Loguru."""

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover - simple bridge
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame: Optional[FrameType] = logging.currentframe()
        depth = 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore[assignment]
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


_LOGGING_CONFIGURED = False


def configure_logger() -> None:
    """Configure Loguru sink and route stdlib logging through it."""
    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED:
        return

    logger.remove()
    logger.add(
        sys.stdout,
        colorize=True,
        enqueue=False,
        level="INFO",
        format="<cyan>{time:HH:mm:ss}</cyan> | <level>{level: <8}</level> | <level>{message}</level>",
    )
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.NOTSET, force=True)
    _LOGGING_CONFIGURED = True


configure_logger()

__all__ = ["logger", "configure_logger"]
