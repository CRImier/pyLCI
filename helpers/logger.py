import logging

def setup_logger(logger_name, log_level="warning"):
    # type: (str, str) -> logging.Logger
    possible_loglevels = ["notset", "debug", "info", "warning", "error", "critical"]
    if log_level.lower() not in possible_loglevels:
        raise ValueError("Wrong loglevel passed while creating '{}' logger: {}".format(logger_name, log_level))
    logger_level_attr = getattr(logging, log_level.upper())
    logger = logging.getLogger(logger_name)
    logger.setLevel(logger_level_attr)
    return logger
