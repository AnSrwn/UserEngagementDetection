from enum import Enum
from threading import Thread
from dask.distributed import Client

from twisted.internet import task, reactor

from common.log import Logger
from processing.futures_queue import FuturesQueue


class FrequencyStatus(Enum):
    STOPPED = "stopped"
    RUNNING = "running"


class PredictionFrequency:
    status = FrequencyStatus.STOPPED
    dask_client = None
    futures_queue: FuturesQueue = None
    thread = None
    prediction_frequency_task = None
    prediction_frequency_default = 1
    prediction_frequency = 1
    previous_process_count = 0

    def adjust_prediction_frequency(self):
        try:
            process_count = self.futures_queue.length()

            if (self.previous_process_count > 10) & (process_count > self.previous_process_count):
                self.prediction_frequency += process_count

            if (self.previous_process_count < 10) & (process_count < 10):
                self.prediction_frequency = self.prediction_frequency_default

            self.previous_process_count = process_count
            Logger.instance().info(
                f"Processes in queue: {process_count} | Prediction Frequency: {self.prediction_frequency}")
        except Exception as e:
            Logger.instance().error(f"adjust_prediction_frequency: {e}")

    def run_prediction_frequency_loop(self):
        self.prediction_frequency_task = task.LoopingCall(self.adjust_prediction_frequency)
        d = self.prediction_frequency_task.start(5.0)  # call every 5 seconds
        d.addErrback(lambda reason: Logger.instance().error(f"adjust_prediction_frequency: {reason}"))

        try:
            reactor.run(installSignalHandlers=False)
        except Exception as e:
            Logger.instance().error(f"Reactor is already running: {e}")

    def create_thread(self):
        return Thread(target=self.run_prediction_frequency_loop)

    def __init__(self, dask_client: Client):
        self.dask_client = dask_client
        self.futures_queue = FuturesQueue.instance()
        self.thread = self.create_thread()

    def get_frequency(self):
        return self.prediction_frequency

    def start_thread(self):
        Logger.instance().info(f"Starting prediction_frequency...: FrequencyStatus: {self.status}")
        if self.status == FrequencyStatus.STOPPED:
            if self.thread is None:
                self.thread = self.create_thread()

            if not self.thread.is_alive():
                self.thread.start()

            self.status = FrequencyStatus.RUNNING

        Logger.instance().info(f"Started prediction_frequency: FrequencyStatus: {self.status}")

    def stop_thread(self):
        Logger.instance().info(f"Stopping prediction_frequency...: FrequencyStatus: {self.status}")
        if self.status == FrequencyStatus.RUNNING:
            try:
                self.prediction_frequency_task.stop()
            except Exception as e:
                Logger.instance().error(f"Tried to stop a LoopingCall that was not running: {e}")
            self.thread = None
            # try:
            #     reactor.stop()
            # except Exception as e:
            #     Logger.instance().error(f"Tried to stop a Reactor that was not running: {e}")
            self.status = FrequencyStatus.STOPPED

        Logger.instance().info(f"Stopped prediction_frequency: FrequencyStatus: {self.status}")
