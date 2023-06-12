import argparse
import logging
import asyncio
import ssl
import uuid
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database.models import Test
from database.database import engine, create_db_and_tables
from routers import test
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder, MediaRelay
from pydantic import BaseModel

logger = logging.getLogger("pc")
pcs = set()

app = FastAPI(title="UserEngagementDetection")


#We define authorizations for middleware components
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:3000"],
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

class OfferRequest(BaseModel):
    sdp: str
    type: str

# WebRTC
@app.post("/offer")
async def offer(request: OfferRequest):
    logger.info(request)
    offer = RTCSessionDescription(sdp=request.sdp, type=request.type)

    pc = RTCPeerConnection()
    pc_id = "PeerConnection(%s)" % uuid.uuid4()
    pcs.add(pc)

    def log_info(msg, *args):
        logger.info(pc_id + " " + msg, *args)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        log_info("Connection state is %s", pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    @pc.on("track")
    def on_track(track):
        log_info("Track %s received", track.kind)

        # if track.kind == "video":
            # pc.addTrack(
            #     VideoTransformTrack(
            #         relay.subscribe(track), transform=params["video_transform"]
            #     )
            # )
            # if args.record_to:
            #     recorder.addTrack(relay.subscribe(track))

        @track.on("ended")
        async def on_ended():
            log_info("Track %s ended", track.kind)
            # await recorder.stop()

    # handle offer
    await pc.setRemoteDescription(offer)

    # send answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return pc.localDescription
