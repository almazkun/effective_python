import sys
import logging
from contextlib import contextmanager

logging.basicConfig(stream=sys.stdout, level=logging.WARNING)


@contextmanager
def log_level(level, name):
    logger = logging.getLogger(name)
    old_level = logger.getEffectiveLevel()
    logger.setLevel(level)
    try:
        yield logger
    finally:
        logger.setLevel(old_level)


with log_level(logging.DEBUG, "my_log") as logger:
    logger.debug(f" * This is a message for {logger.name}!")
    logging.debug("This will not print")


logger = logging.getLogger("my_log")
logger.debug("Debug will not print")
logger.error("Error will print")


with log_level(logging.DEBUG, "other-log") as logger:
    logger.debug(f"This is a message for {logger.name}!")
    logging.debug("This will not print")
