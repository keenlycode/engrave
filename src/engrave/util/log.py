# lib: built-in
import sys
import os
import logging


def getLogger(name=None) -> logging.Logger:
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    if name:
        log_level = 'NOTSET'
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # stdout handler for INFO, DEBUG
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.addFilter(lambda r: r.levelno < logging.WARNING)

    # stderr handler for WARNING+
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)

    fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    stdout_handler.setFormatter(fmt)
    stderr_handler.setFormatter(fmt)

    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)

    return logger
