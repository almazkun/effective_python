import logging
from contextlib import contextmanager

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
    l = logging.getLogger()
    print(l.getEffectiveLevel())
    l.setLevel(logging.WARNING)
    logging.error("error")
    print(l.getEffectiveLevel())
    logger.debug(f" * This will be printed to the {logger.name} logger!")
    logging.debug("This printed will not")

print("done")