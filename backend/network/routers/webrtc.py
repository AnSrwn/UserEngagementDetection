import logging
import uuid
import concurrent.futures
import multiprocessing

from fastapi import APIRouter
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaRelay

from network.models.offer_request import OfferRequest
from processing.engagement_detection import VideoTransformTrack

log = logging.getLogger("uvicorn.debug")

router = APIRouter()

peerConnections = set()
relay = MediaRelay()

log.info(f"Number of cores: {multiprocessing.cpu_count()}")

processExcecutor = concurrent.futures.ProcessPoolExecutor(
    mp_context=multiprocessing.get_context("spawn")
)


@router.post("/offer", response_model=RTCSessionDescription)
async def offer(request: OfferRequest):
    """This endpoint is used to establish a WebRTC connection."""
    log.info(request)
    offer = RTCSessionDescription(sdp=request.sdp, type=request.type)

    pc = RTCPeerConnection()
    pc_id = f"pc_{uuid.uuid1()}"
    peerConnections.add(pc)

    def log_info(msg, *args):
        log.info(pc_id + " " + msg, *args)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        log_info("Connection state is %s", pc.connectionState)
        if pc.connectionState == "failed":
            log_info("Connection state is %s", pc.connectionState)
            await pc.close()
            peerConnections.discard(pc)

    @pc.on("track")
    def on_track(track):
        log_info("Track %s received", track.kind)

        if track.kind == "video":
            # return same video
            pc.addTrack(
                VideoTransformTrack(relay.subscribe(track), pc_id, processExcecutor)
            )

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
