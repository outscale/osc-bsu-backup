import logging
import sys


def setup_logging(name=None, level=logging.INFO):
    logger = logging.getLogger(name)
    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
    logger.addHandler(stream)
    logger.setLevel(level=level)
    return logger
