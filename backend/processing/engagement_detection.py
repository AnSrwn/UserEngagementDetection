import logging
from datetime import datetime
from dask.distributed import Client

import cv2
import dlib
import keras
import msgpack
import msgpack_numpy
import numpy
from aiortc import MediaStreamTrack
from numpy import mat as matrix

from common.log import Logger
from processing.futures_queue import FuturesQueue
from composables.prediction_frequency import PredictionFrequency
from database.database_service import DatabaseService
from database.models import Engagement

engagement_model = keras.models.load_model("processing/models/parallel_model.h5", compile=False)
Logger.instance().info("Engagement Model loaded")


class VideoTransformTrack(MediaStreamTrack):
    kind = "video"
    pc_id: str = None
    frame_counter = 0
    dask_client = None
    futures_queue = None
    prediction_frequency = None

    def __init__(self, track, pc_id: str, dask_client: Client, prediction_frequency: PredictionFrequency):
        super().__init__()
        self.track = track
        self.pc_id = pc_id
        self.dask_client = dask_client
        self.futures_queue = FuturesQueue.instance()
        self.prediction_frequency = prediction_frequency

    def future_callback(self, fn):
        try:
            fn.release()
            self.futures_queue.remove(fn.key)
            self.dask_client.cancel(fn, force=True)
            del fn
        except Exception as e:
            return f"future_callback: {e}"

    async def recv(self):
        frame = await self.track.recv()

        self.frame_counter += 1

        if self.frame_counter >= self.prediction_frequency.get_frequency():
            self.frame_counter = 0

            # Special serialization and deserialization to use the image in another process
            image: matrix = frame.to_ndarray(format="bgr24")
            serialized = msgpack.packb(image, default=msgpack_numpy.encode)

            try:
                big_future = self.dask_client.scatter(serialized)
                future = self.dask_client.submit(detect_engagement, big_future, self.pc_id)
                future.add_done_callback(self.future_callback)
                self.futures_queue.add(future.key, future)

                # del image  # del serialized
            except Exception as e:
                Logger.instance().error(f"recv: {e}")
                Logger.instance().info("Shutdown Dask Client...")
                self.dask_client.cancel()
                Logger.instance().info("Restart Dask Client...")
                self.dask_client.restart()
                Logger.instance().info("Dask Client restarted.")

        return frame


def detect_engagement(serialized, pc_id: str):
    logging.basicConfig(filename='multi-processing.log', level=logging.DEBUG)
    process_logger = logging.getLogger()

    try:
        frame_time = datetime.now().isoformat()
        image = msgpack.unpackb(serialized, object_hook=msgpack_numpy.decode)
        # del serialized
        detector = dlib.get_frontal_face_detector()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        roi = []
        for face in faces:
            x1 = face.left()
            y1 = face.top()
            x2 = face.right()
            y2 = face.bottom()

            # if no face detected, skip predictionsF
            if (len(image[y1:y2, x1:x2]) <= 0 or len(image[y1 - 100: y2 + 100, x1 - 100: x2 + 100]) <= 0):
                # del image
                return "No face detected"

            # resize image to face dimensions and convert to gray image
            roi.append(cv2.resize(cv2.cvtColor(image[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY), (48, 48)))
            # del image

            # get predictions
            if len(roi) > 0:
                # add dimension, because model expects multiple images
                images = numpy.expand_dims(roi, axis=3)
                predictions = engagement_model.predict(images)
                roi = []

                # retrieve predictions
                boredom = predictions[0][0][1] * 100
                engagement = predictions[1][0][1] * 100
                confusion = predictions[2][0][1] * 100
                frustration = predictions[3][0][1] * 100

                with DatabaseService() as db_service:
                    db_service.engagement.add(
                        Engagement(peer_connection=pc_id, time=frame_time, boredom=round(boredom, 4),
                                   engagement=round(engagement, 4), confusion=round(confusion, 4),
                                   frustration=round(frustration, 4), ))
                    db_service.commit()
                    db_service.close()  # TODO: not really needed

                return (f"{pc_id}: Boredom: {boredom} | Engagement: {engagement} | Confusion: {confusion} | "
                        f"Frustration: {frustration}")
            else:
                # del image
                return "No face detected"

    except UnboundLocalError as e:
        # del image
        process_logger.exception(f"No predictions: {e}")
        return f"No predictions: {e}"
    except Exception as e:
        # del image
        process_logger.exception(f"detectEngagement: {e}")
        return f"detectEngagement: {e}"

    return None
