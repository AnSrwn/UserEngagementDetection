import logging
import uuid

from fastapi import FastAPI, HTTPException
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


#We define authorizations for middleware components
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://localhost:3000",
        "https://localhost:8000",
        "https://localhost:3000",
        "https://127.0.0.1:8000",
        "https://127.0.0.1:3000",
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
            pc.addTrack(track)

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
