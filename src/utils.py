import logging
import sys

def setup_logger(name=None):
    logger = logging.getLogger(name if name else __name__)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    handler.setFormatter(formatter)
    if not logger.hasHandlers():
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

cities_code = ["0{}".format(i) for i in range(10)] + [str(i) for i in range(10, 100)]