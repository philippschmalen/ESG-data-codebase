import logging


def logger():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "[%(asctime)s]-[%(name)s]-[%(levelname)s] - %(message)s"
    )
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    logging.basicConfig(filename="debug.log")
    return root_logger
