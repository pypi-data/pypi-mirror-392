import logging

def get_logger(name: str):
    if not logging.getLogger().handlers:
        fmt = "[%(asctime)s] [%(levelname)s] %(message)s"
        logging.basicConfig(level=logging.INFO, format=fmt, datefmt="%H:%M:%S")
    return logging.getLogger(name)
