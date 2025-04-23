import sys

from loguru import logger


def setup_logger():
    logger.remove()
    # STDOUT cant be used as a sink because it will break the stream
    # logger.add(
    #     sink=sys.stdout,
    #     level="INFO",
    # )
    # STDERR
    logger.add(
        sink=sys.stderr,
        level="INFO",
    )
