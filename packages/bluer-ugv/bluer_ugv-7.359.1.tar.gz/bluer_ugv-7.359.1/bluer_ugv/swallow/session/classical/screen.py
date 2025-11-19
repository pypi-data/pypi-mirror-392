from bluer_options.host.functions import is_headless

from bluer_ugv.logger import logger


class ClassicalScreen:
    def __init__(self):
        if is_headless():
            return

        logger.info(f"{self.__class__.__name__} created.")
