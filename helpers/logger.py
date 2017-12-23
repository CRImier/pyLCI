import logging

def setup_logger(logger_name, log_level="warning"):
    # type: (str, str) -> logging.Logger
    # todo : read level from config here
    logger_level_attr = getattr(logging, log_level.upper())
    logger = logging.getLogger(logger_name)
    logger.setLevel(logger_level_attr)
    return logger
