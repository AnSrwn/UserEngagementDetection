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
    # Defines how often predictions are made. Every x frames.
    prediction_frequency = 20
    previous_process_count = 0

    def adjust_prediction_frequency(self):
        process_count = len(self.executor._pending_work_items)

        if (self.previous_process_count > 10) & (process_count > 10):
            self.prediction_frequency += process_count

        if (self.previous_process_count < 10) & (process_count < 10):
            self.prediction_frequency = 20

        self.previous_process_count = process_count
        # log.info(f"Processes in queue: {process_count} | Prediction Frequency: {self.prediction_frequency}")

    def run_prediction_frequency_loop(self):
        self.prediction_frequency_task = task.LoopingCall(self.adjust_prediction_frequency)
        self.prediction_frequency_task.start(5.0)  # call every 5 seconds

        reactor.run(installSignalHandlers=False)

    def __init__(self, executor: concurrent.futures.ProcessPoolExecutor, ):
        self.executor = executor
        self.thread = Thread(target=self.run_prediction_frequency_loop)

    def get_frequency(self):
        return self.prediction_frequency

    def start_thread(self):
        if self.status == FrequencyStatus.STOPPED:
            if not self.thread.is_alive():
                self.thread.start()
                self.status = FrequencyStatus.RUNNING

    def stop_thread(self):
        if self.status == FrequencyStatus.RUNNING:
            self.prediction_frequency_task.stop()
            self.thread.join()
            self.thread = None
            reactor.stop()
            self.status = FrequencyStatus.STOPPED
