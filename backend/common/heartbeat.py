import time
import asyncio
import logging

log = logging.getLogger("uvicorn.debug")


async def heartbeat():
    """The heartbeat() function is used to test the efficiency of tasks, threads and processes."""
    while True:
        start = time.time()
        await asyncio.sleep(1)
        delay = time.time() - start - 1
        log.info(f"heartbeat delay = {delay:.3f}s")
