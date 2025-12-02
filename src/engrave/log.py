# lib: built-in
import sys
import os
import logging


log_level = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    stream=sys.stdout,
    level=log_level,
    format="[%(asctime)s] [%(levelname)s] %(message)s"
)


def getLogger(name) -> logging.Logger:
    return logging.getLogger(name)
