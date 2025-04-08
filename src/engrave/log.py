# lib: built-in
import sys

# lib: external
from loguru import logger


def configure(*levels):
    """Configure loguru logger with a nice format."""
    log_format = (
        "<level>{level: <8}</level> | "
        "<level>{message}</level>"
    )
    for level in levels:
        logger.add(sys.stderr, format=log_format, level=level.upper(), diagnose=False)
