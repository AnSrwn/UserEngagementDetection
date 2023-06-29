import asyncio
from asyncore import loop
import io
import logging
import time
import uuid
import keras
import cv2
import dlib
import numpy
import multiprocessing, time, signal
import msgpack
import msgpack_numpy as m

from fastapi import FastAPI, BackgroundTasks
from fastapi.logger import logger
from fastapi.middleware.cors import CORSMiddleware
from database.models import Test
from database.database import engine, create_db_and_tables
from common.DillProcess import DillProcess
from routers import test
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder, MediaRelay
from pydantic import BaseModel
from multiprocessing import Process
from numpy import mat as Matrix

log = logging.getLogger('uvicorn.debug')
# log.setLevel('DEBUG')

app = FastAPI(title="UserEngagementDetection")
log.info("FastAPI started")

engagementModel = keras.models.load_model('models/parallel_model.h5')
log.info("Engagement Model loaded")


# We define authorizations for middleware components
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://localhost:3000"
        ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# use heartbeat to test efficiency of background tasks
async def heartbeat():
    while True:
        start = time.time()
        await asyncio.sleep(1)
        delay = time.time() - start - 1
        log.info(f'heartbeat delay = {delay:.3f}s')


#We use a callback to trigger the creation of the table if they don't exist yet
#When the API is starting
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # use heartbeat to test efficiency of background tasks
    asyncio.create_task(heartbeat())

app.include_router(test.router)

@app.get("/")
async def root():
    return {"message": "UserEngagementDetection API is working."}

# WebRTC
pcs = set()
relay = MediaRelay()

class OfferRequest(BaseModel):
    sdp: str
    type: str

@app.post("/offer")
async def offer(request: OfferRequest):
    log.info(request)
    offer = RTCSessionDescription(sdp=request.sdp, type=request.type)

    pc = RTCPeerConnection()
    pc_id = "PeerConnection(%s)" % uuid.uuid4()
    pcs.add(pc)

    def log_info(msg, *args):
        log.info(pc_id + " " + msg, *args)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        log_info("Connection state is %s", pc.connectionState)
        if pc.connectionState == "failed":
            log_info("Connection state is %s", pc.connectionState)
            await pc.close()
            pcs.discard(pc)

    @pc.on("track")
    def on_track(track):
        log_info("Track %s received", track.kind)

        if track.kind == "video":
            # return same video
            pc.addTrack(VideoTransformTrack(
                relay.subscribe(track),
                pc_id
            ))

        @track.on("ended")
        async def on_ended():
            log_info("Track %s ended", track.kind)

    # handle offer
    await pc.setRemoteDescription(offer)
    log.info("RemoteDescription: " + str(offer))

    # send answer
    answer = await pc.createAnswer()
    log.info("Answer: " + str(answer))
    await pc.setLocalDescription(answer)
    log.info("LocalDescription: " + str(pc.localDescription))

    return pc.localDescription

def detectEngagement(serialized):
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
            if len(image[y1:y2, x1:x2]) <= 0 or len(image[y1-100:y2+100, x1-100:x2+100]) <= 0:
                log.info('No face detected')
                return
            # append faces
            roi.append(cv2.resize(cv2.cvtColor(image[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY), (48,48)))
            # get predictions
            predictions = []
            if len(roi)>0:
                test_images = numpy.expand_dims(roi, axis=3)
                predictions = engagementModel.predict(test_images)

                boredom = round(predictions[0][0][1],3)
                engagement = round(predictions[1][0][1],3)
                confusion = round(predictions[2][0][1],3)
                frustration = round(predictions[3][0][1],3)

                log.info(f"test: Boredem: {boredom} | Engagement: {engagement} | Confusion: {confusion} | Frustration: {frustration}")

    except UnboundLocalError as e:
        # if no predictions
        log.error(f"No predictions: {e}")
    except Exception as e:
        log.error(f"detectEngagement: {e}")


# A video stream track that transforms frames from an another track.
class VideoTransformTrack(MediaStreamTrack):

    kind = "video"
    pc_id = None
    frame_counter = 0
    queue = None
    workers = None

    async def worker(self):
        while True:
            coro = await self.queue.get()
            await coro  # consider using try/except
            self.queue.task_done()

    async def start_queue(self):
        self.queue.get_nowait()
    

    def __init__(self, track, pc_id):
        super().__init__()  # don't forget this!
        self.track = track
        self.pc_id = pc_id
        # self.queue = asyncio.Queue(maxsize=1)
        # self.workers = [asyncio.create_task(self.worker()) for _ in range(1)]
        # self.start_queue()

    async def recv(self):
        frame = await self.track.recv()
        image: Matrix = frame.to_ndarray(format="bgr24")
        serialized = msgpack.packb(image, default=m.encode)
        self.frame_counter += 1

        if (self.frame_counter == 20):
            self.frame_counter = 0
            # await self.queue.put(self.detectEngagement(frame))
            try:
                process = Process(target=detectEngagement, args=(serialized,))
                process.start()
                log.info(f"{process.name}, isAlive: {process.is_alive()}")
            except Exception as e:
                log.error(f"recv: {e}")

        return frame