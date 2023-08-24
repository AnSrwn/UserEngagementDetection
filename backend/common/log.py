import logging

from common.singleton import Singleton


@Singleton
class Logger:
    logger = None

    def __init__(self):
        self.logger = logging.getLogger("uvicorn.debug")

    def info(self, text):
        return self.logger.info(text)

    def error(self, text):
        return self.logger.info(text)
