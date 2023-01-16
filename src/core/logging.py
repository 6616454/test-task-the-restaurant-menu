import logging


def setup_logging():
    logger = logging.getLogger('main_logger')
    stream_handler = logging.StreamHandler()
    logger.addHandler(stream_handler)
    stream_formatter = logging.Formatter(
        '%(asctime)s - %(funcName)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(stream_formatter)
    logger.setLevel(logging.DEBUG)
    return logger
