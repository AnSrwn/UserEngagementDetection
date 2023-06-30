from database.models import Engagement
from database.database_service import DatabaseService
import msgpack
import msgpack_numpy as m
import cv2
import dlib
import numpy
import logging
import keras
import concurrent.futures

from aiortc import MediaStreamTrack
from numpy import mat as Matrix
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP


log = logging.getLogger("uvicorn.debug")

engagementModel = keras.models.load_model(
    "processing/models/parallel_model.h5", compile=False
)
log.info("Engagement Model loaded")

with DatabaseService() as db_service:
    # A video stream track that transforms frames from an another track.
    class VideoTransformTrack(MediaStreamTrack):
        kind = "video"
        pc_id: str = None
        frame_counter = 0
        # queue = None
        # workers = None
        processExcecutor = None

        async def worker(self):
            while True:
                coro = await self.queue.get()
                await coro  # consider using try/except
                self.queue.task_done()

        async def start_queue(self):
            self.queue.get_nowait()

        def __init__(
            self,
            track,
            pc_id: str,
            processExcecutor: concurrent.futures.ProcessPoolExecutor,
        ):
            super().__init__()  # don't forget this!
            self.track = track
            self.pc_id = pc_id
            self.processExcecutor = processExcecutor
            # self.queue = asyncio.Queue(maxsize=1)
            # self.workers = [asyncio.create_task(self.worker()) for _ in range(1)]
            # self.start_queue()

        async def recv(self):
            frame = await self.track.recv()
            image: Matrix = frame.to_ndarray(format="bgr24")
            serialized = msgpack.packb(image, default=m.encode)
            self.frame_counter += 1

            if self.frame_counter == 20:
                self.frame_counter = 0
                # await self.queue.put(self.detectEngagement(frame))
                try:
                    # TODO: Maybe use Tasks or Threads to optimize synchronous flow
                    process = self.processExcecutor.submit(
                        detectEngagement, serialized, self.pc_id
                    )
                except Exception as e:
                    log.error(f"recv: {e}")

            return frame

    def detectEngagement(serialized, pc_id: str):
        try:
            image = msgpack.unpackb(serialized, object_hook=m.decode)
            detector = dlib.get_frontal_face_detector()
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)

            roi = []
            for face in faces:
                x1 = face.left()
                y1 = face.top()
                x2 = face.right()
                y2 = face.bottom()
                # if no face skip predictions
                if (
                    len(image[y1:y2, x1:x2]) <= 0
                    or len(image[y1 - 100 : y2 + 100, x1 - 100 : x2 + 100]) <= 0
                ):
                    return "No face detected"
                # append faces
                roi.append(
                    cv2.resize(
                        cv2.cvtColor(image[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY), (48, 48)
                    )
                )
                # get predictions
                predictions = []
                if len(roi) > 0:
                    test_images = numpy.expand_dims(roi, axis=3)
                    predictions = engagementModel.predict(test_images)

                    boredom = predictions[0][0][1] * 100
                    engagement = predictions[1][0][1] * 100
                    confusion = predictions[2][0][1] * 100
                    frustration = predictions[3][0][1] * 100

                    db_service.engagement.add(
                        Engagement(
                            peer_connection=pc_id,
                            time=datetime.now(),
                            boredom=round(boredom, 4),
                            engagement=round(engagement, 4),
                            confusion=round(confusion, 4),
                            frustration=round(frustration, 4),
                        )
                    )
                    db_service.commit()

                    return f"{pc_id}: Boredem: {boredom} | Engagement: {engagement} | Confusion: {confusion} | Frustration: {frustration}"
                else:
                    return "No face detected"

        except UnboundLocalError as e:
            return f"No predictions: {e}"
        except Exception as e:
            return f"detectEngagement: {e}"

        return None
