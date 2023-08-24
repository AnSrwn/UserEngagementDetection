import logging

from common.singleton import Singleton


@Singleton
class FuturesQueue:
    futures = None

    log = logging.getLogger("uvicorn.debug")

    def __init__(self):
        self.futures = {}

    def add(self, key, future):
        self.futures[key] = future

    def remove(self, key):
        self.futures.pop(key)

    def length(self) -> int:
        return len(self.futures.items())
