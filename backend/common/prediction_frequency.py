import concurrent.futures
import logging
from enum import Enum
from threading import Thread

from twisted.internet import task, reactor

log = logging.getLogger("uvicorn.debug")


class FrequencyStatus(Enum):
    STOPPED = "stopped"
    RUNNING = "running"


class PredictionFrequency:
    status = FrequencyStatus.STOPPED
    executor = None
    thread = None
    prediction_frequency_task = None
    prediction_frequency_default = 20
    # Defines how often predictions are made. Every x frames.
    prediction_frequency = 20
    previous_process_count = 0

    def adjust_prediction_frequency(self):
        try:
            process_count = len(self.executor._pending_work_items)

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

    def __init__(self, executor: concurrent.futures.ProcessPoolExecutor, ):
        self.executor = executor
        self.thread = self.create_thread()

    def get_frequency(self):
        return self.prediction_frequency

    def start_thread(self):
        if self.status == FrequencyStatus.STOPPED:
            if self.thread is None:
                self.thread = self.create_thread()

            if not self.thread.is_alive():
                self.thread.start()

            self.status = FrequencyStatus.RUNNING

    def stop_thread(self):
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
