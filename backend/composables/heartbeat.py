import time
import asyncio

from common.log import Logger


async def heartbeat():
    """The heartbeat() function is used to test the efficiency of tasks, threads and processes."""
    while True:
        start = time.time()
        await asyncio.sleep(1)
        delay = time.time() - start - 1
        Logger.instance().info(f"heartbeat delay = {delay:.3f}s")
