from database.models import Engagement
from database.database_service import DatabaseService
import msgpack
import msgpack_numpy
import cv2
import dlib
import numpy
import logging
import keras
import concurrent.futures

from aiortc import MediaStreamTrack
from numpy import mat as matrix
from datetime import datetime

log = logging.getLogger("uvicorn.debug")

engagementModel = keras.models.load_model(
    "processing/models/parallel_model.h5", compile=False
)
log.info("Engagement Model loaded")

with DatabaseService() as db_service:
    class VideoTransformTrack(MediaStreamTrack):
        kind = "video"
        pc_id: str = None
        frame_counter = 0
        process_executor = None

        def __init__(
                self,
                track,
                pc_id: str,
                process_executor: concurrent.futures.ProcessPoolExecutor,
        ):
            super().__init__()
            self.track = track
            self.pc_id = pc_id
            self.process_executor = process_executor

        async def recv(self):
            frame = await self.track.recv()

            # Special serialization and deserialization to use the image in another process
            image: matrix = frame.to_ndarray(format="bgr24")
            serialized = msgpack.packb(image, default=msgpack_numpy.encode)

            self.frame_counter += 1

            if self.frame_counter == 20:
                self.frame_counter = 0

                try:
                    process = self.process_executor.submit(
                        detect_engagement, serialized, self.pc_id
                    )
                except Exception as e:
                    log.error(f"recv: {e}")

            return frame


    def detect_engagement(serialized, pc_id: str):
        try:
            frame_time = datetime.now().isoformat()
            image = msgpack.unpackb(serialized, object_hook=msgpack_numpy.decode)
            detector = dlib.get_frontal_face_detector()
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)

            roi = []
            for face in faces:
                x1 = face.left()
                y1 = face.top()
                x2 = face.right()
                y2 = face.bottom()

                # if no face detected, skip predictions
                if (
                        len(image[y1:y2, x1:x2]) <= 0
                        or len(image[y1 - 100: y2 + 100, x1 - 100: x2 + 100]) <= 0
                ):
                    return "No face detected"

                # resize image to face dimensions and convert to gray image
                roi.append(
                    cv2.resize(
                        cv2.cvtColor(image[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY), (48, 48)
                    )
                )

                # get predictions
                if len(roi) > 0:
                    # add dimension, because model expects multiple images
                    images = numpy.expand_dims(roi, axis=3)
                    predictions = engagementModel.predict(images)

                    # retrieve predictions
                    boredom = predictions[0][0][1] * 100
                    engagement = predictions[1][0][1] * 100
                    confusion = predictions[2][0][1] * 100
                    frustration = predictions[3][0][1] * 100

                    db_service.engagement.add(
                        Engagement(
                            peer_connection=pc_id,
                            time=frame_time,
                            boredom=round(boredom, 4),
                            engagement=round(engagement, 4),
                            confusion=round(confusion, 4),
                            frustration=round(frustration, 4),
                        )
                    )
                    db_service.commit()

                    return (f"{pc_id}: Boredom: {boredom} | Engagement: {engagement} | Confusion: {confusion} | "
                            f"Frustration: {frustration}")
                else:
                    return "No face detected"

        except UnboundLocalError as e:
            return f"No predictions: {e}"
        except Exception as e:
            return f"detectEngagement: {e}"

        return None
