import logging


def setup_logger(logger_name, log_level):
    # type: (str, str) -> logging.Logger
    level = get_log_level(log_level, logging.WARNING)
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    return logger


def get_log_level(log_level_name, default_value):
    # type: (str, int) -> int
    """
    Returns the log level based on a string name
    >>> get_log_level("warning", logging.ERROR) == logging.WARNING
    True
    >>> get_log_level("warning???", logging.ERROR) == logging.ERROR
    True
    """
    try:
        return logging._checkLevel(log_level_name.upper())
    except ValueError:
        return default_value
