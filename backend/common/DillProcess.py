import logging
import dill
from multiprocessing import Process

log = logging.getLogger('uvicorn.debug')

class DillProcess(Process):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Save the target function as bytes, using dill
        try:
            self._target = dill.dumps(self._target)
        except Exception as e:
            log.error(f"DillProcess | init: {e}")

    def run(self):
        if self._target:
            # Unpickle the target function before executing
            try:
                self._target = dill.loads(self._target)
            except Exception as e:
                log.error(f"DillProcess | load: {e}")
            # Execute the target function
            try:
                self._target(*self._args, **self._kwargs)
            except Exception as e:
                log.error(f"DillProcess | execute: {e}")
