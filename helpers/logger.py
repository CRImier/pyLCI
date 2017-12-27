import logging


def setup_logger(logger_name, log_level="warning"):
    # type: (str, str) -> logging.Logger
    try:
        logger_level_attr = getattr(logging, log_level.upper())
    except AttributeError:
        logger_level_attr = logging.WARNING

    logger = logging.getLogger(logger_name)
    logger.setLevel(logger_level_attr)
    return logger
