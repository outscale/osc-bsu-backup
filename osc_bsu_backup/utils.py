import logging
import sys


def setup_logging(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
    logger.addHandler(stream)
    logger.setLevel(level=level)
    return logger
