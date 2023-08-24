from datetime import datetime, timedelta
from enum import Enum
from threading import Thread

from twisted.internet import task, reactor

from common.log import Logger
from database.database_service import DatabaseService


class FrequencyStatus(Enum):
    STOPPED = "stopped"
    RUNNING = "running"


class DatabaseCleaner:
    status = FrequencyStatus.STOPPED
    executor = None
    thread = None
    task = None

    def clean_database(self):
        try:
            with DatabaseService() as db_service:
                current_time = datetime.now()
                one_day_ago = (current_time - timedelta(days=1)).isoformat()

                deleted_rows_count = db_service.engagement.delete_old_data(one_day_ago)
                Logger.instance().info(f"database_cleaner: Deleted rows: {deleted_rows_count}")
        except Exception as e:
            Logger.instance().error(f"database_cleaner: Failed to delete data: {e}")

    def run_clean_database_loop(self):
        self.task = task.LoopingCall(self.clean_database)
        self.task.start(24.0 * 60.0 * 60.0)  # call every 24 hours

        try:
            reactor.run(installSignalHandlers=False)
        except Exception as e:
            Logger.instance().error(f"database_cleaner: Reactor is already running: {e}")

    def create_thread(self):
        return Thread(target=self.run_clean_database_loop)

    def __init__(self):
        self.thread = self.create_thread()

    def start_thread(self):
        Logger.instance().info(f"database_cleaner: Starting...: Status: {self.status}")
        if self.status == FrequencyStatus.STOPPED:
            if self.thread is None:
                self.thread = self.create_thread()

            if not self.thread.is_alive():
                self.thread.start()

            self.status = FrequencyStatus.RUNNING

        Logger.instance().info(f"database_cleaner: Started: Status: {self.status}")

    def stop_thread(self):
        Logger.instance().info(f"database_cleaner: Stopping...: Status: {self.status}")
        if self.status == FrequencyStatus.RUNNING:
            try:
                self.task.stop()
            except Exception as e:
                Logger.instance().error(f"database_cleaner: Tried to stop a LoopingCall that was not running: {e}")

            self.thread = None
            self.status = FrequencyStatus.STOPPED

        Logger.instance().info(f"database_cleaner: Stopped: Status: {self.status}")
