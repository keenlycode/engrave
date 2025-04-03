# lib: built-in
import sys

# lib: external
from loguru import logger


def configure(level: str):
    """Configure loguru logger with a nice format."""
    logger.remove()
    log_format = (
        "<level>{level: <8}</level> | "
        "<level>{message}</level>"
    )
    logger.add(sys.stderr, format=log_format, level=level.upper(), diagnose=False)
