import logging


def setup_logger(logger_name, logger_level=logging.WARNING):
    # type: (str, int) -> logging.Logger
    # todo : read level from config here
    logger = logging.getLogger(logger_name)
    logger.setLevel(logger_level)
    return logger
