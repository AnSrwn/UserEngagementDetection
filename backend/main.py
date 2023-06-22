import asyncio
import logging
import time
import uuid
import keras
import cv2
import dlib
import numpy
import concurrent.futures

from fastapi import FastAPI, BackgroundTasks
from fastapi.logger import logger
from fastapi.middleware.cors import CORSMiddleware
from database.models import Test
from database.database import engine, create_db_and_tables
from routers import test
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder, MediaRelay
from pydantic import BaseModel

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

#We use a callback to trigger the creation of the table if they don't exist yet
#When the API is starting
@app.on_event("startup")
def on_startup():
    create_db_and_tables()


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
                relay.subscribe(track)
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

# A video stream track that transforms frames from an another track.
class VideoTransformTrack(MediaStreamTrack):

    kind = "video"
    # background_tasks = BackgroundTasks()
    # loop = asyncio.get_event_loop()
    # background_tasks = None

    def __init__(self, track):
        super().__init__()  # don't forget this!
        self.track = track

    async def detectEngagement(self, frame):
        image = frame.to_ndarray(format="bgr24")

        try:
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
                    return frame
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

                    log.info(f"Boredem: {boredom} | Engagement: {engagement} | Confusion: {confusion} | Frustration: {frustration}")

        except UnboundLocalError as e:
            # if no predictions
            log.error(f"No predictions: {e}")
        except Exception as e:
            log.error(e)

    async def long_process(self):
        await asyncio.sleep(10)
        log.info("has been processed.")

    async def recv(self):
        frame = await self.track.recv()
        # asyncio.ensure_future(self.long_process())
        # asyncio.ensure_future(self.detectEngagement(frame))
        # asyncio.run(self.long_process())
        # with concurrent.futures.ProcessPoolExecutor() as executor:
        #     executor.submit(self.long_process)
        # asyncio.create_task(self.long_process())
        asyncio.create_task(self.detectEngagement(frame))
        asyncio.sleep(0) # suspend to start task
        return frame