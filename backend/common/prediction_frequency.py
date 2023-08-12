import concurrent.futures
import logging
from enum import Enum
from threading import Thread
from dask.distributed import Client, Future

from twisted.internet import task, reactor

log = logging.getLogger("uvicorn.debug")


class FrequencyStatus(Enum):
    STOPPED = "stopped"
    RUNNING = "running"


class PredictionFrequency:
    status = FrequencyStatus.STOPPED
    executor = None
    pending_futures = {}
    thread = None
    prediction_frequency_task = None
    prediction_frequency_default = 30
    prediction_frequency = 30
    previous_process_count = 0

    def adjust_prediction_frequency(self):
        try:
            # for key, value in self.pending_futures.items():
            #     log.info(key)

            process_count = len(self.pending_futures.items())

            if (self.previous_process_count > 10) & (process_count > self.previous_process_count):
                self.prediction_frequency += process_count

            if (self.previous_process_count < 10) & (process_count < 10):
                self.prediction_frequency = self.prediction_frequency_default

            self.previous_process_count = process_count
            log.info(f"Processes in queue: {process_count} | Prediction Frequency: {self.prediction_frequency}")
        except Exception as e:
            log.error(f"adjust_prediction_frequency: {e}")

    def run_prediction_frequency_loop(self):
        self.prediction_frequency_task = task.LoopingCall(self.adjust_prediction_frequency)
        self.prediction_frequency_task.start(5.0)  # call every 5 seconds

        try:
            reactor.run(installSignalHandlers=False)
        except Exception as e:
            log.error(f"Reactor is already running: {e}")

    def create_thread(self):
        return Thread(target=self.run_prediction_frequency_loop)

    def __init__(self, executor: Client, pending_futures: dict):
        self.executor = executor
        self.pending_futures = pending_futures
        self.thread = self.create_thread()

    def get_frequency(self):
        return self.prediction_frequency

    def start_thread(self):
        log.info(f"Starting prediction_frequency...: FrequencyStatus: {self.status}")
        if self.status == FrequencyStatus.STOPPED:
            if self.thread is None:
                self.thread = self.create_thread()

            if not self.thread.is_alive():
                self.thread.start()

            self.status = FrequencyStatus.RUNNING

        log.info(f"Started prediction_frequency: FrequencyStatus: {self.status}")

    def stop_thread(self):
        log.info(f"Stopping prediction_frequency...: FrequencyStatus: {self.status}")
        if self.status == FrequencyStatus.RUNNING:
            try:
                self.prediction_frequency_task.stop()
            except Exception as e:
                log.error(f"Tried to stop a LoopingCall that was not running: {e}")
            self.thread = None
            # try:
            #     reactor.stop()
            # except Exception as e:
            #     log.error(f"Tried to stop a Reactor that was not running: {e}")
            self.status = FrequencyStatus.STOPPED

        log.info(f"Stopped prediction_frequency: FrequencyStatus: {self.status}")
