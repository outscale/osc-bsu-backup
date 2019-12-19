import logging
import sys

def setup_logging(name):
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logger = logging.getLogger(name)
    return logger
