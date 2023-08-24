import multiprocessing
import uuid

from aiortc import RTCPeerConnection, RTCSessionDescription
from fastapi import APIRouter
from dask.distributed import Client

from common.log import Logger
from network.peer_connections import PeerConnections
from composables.prediction_frequency import PredictionFrequency
from network.models.webrtc import OfferRequest
from processing.engagement_detection import VideoTransformTrack

router = APIRouter()

Logger.instance().info(f"Number of cores: {multiprocessing.cpu_count()}")

dask_client = Client()
prediction_frequency = PredictionFrequency(dask_client)
prediction_frequency.start_thread()


@router.post("/webrtc/offer", response_model=RTCSessionDescription)
async def offer(request: OfferRequest):
    """This endpoint is used to establish a WebRTC connection."""
    Logger.instance().info(request)
    offer_session_description = RTCSessionDescription(sdp=request.sdp, type=request.type)

    pc = RTCPeerConnection()
    pc_id = f"pc_{uuid.uuid1()}"

    def log_info(msg):
        Logger.instance().info(f"{pc_id}: {msg}")

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            if isinstance(message, str) and message.startswith("client_keep_alive"):
                channel.send("server_keep_alive")

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        log_info(f"Connection state is {pc.connectionState}")
        if pc.connectionState == "failed":
            log_info(f"Connection state is {pc.connectionState}")
            await pc.close()
            PeerConnections.instance().discard(pc)  # if len(peerConnections) < 1:  # prediction_frequency.stop_thread()

    @pc.on("track")
    def on_track(track):
        log_info(f"Track {track.kind} received")

        if track.kind == "video":
            # prediction_frequency.start_thread()
            # return same video
            # relay = MediaRelay()
            # relay.subscribe(track)
            # TODO: addTrack kann wahrscheinlich weg gelassen werden
            pc.addTrack(VideoTransformTrack(track, pc_id, dask_client, prediction_frequency))

        @track.on("ended")
        async def on_ended():
            PeerConnections.instance().discard(pc)
            # if len(peerConnections) < 1:
            #     prediction_frequency.stop_thread()
            log_info(f"Track {track.kind} ended")

    # handle offer
    await pc.setRemoteDescription(offer_session_description)
    Logger.instance().info("RemoteDescription: " + str(offer_session_description))

    # send answer
    answer = await pc.createAnswer()
    Logger.instance().info("Answer: " + str(answer))
    await pc.setLocalDescription(answer)
    Logger.instance().info("LocalDescription: " + str(pc.localDescription))

    PeerConnections.instance().add(pc)
    return pc.localDescription
