from pydantic import BaseModel
from aiortc import RTCSessionDescription


class OfferRequest(BaseModel):
    sdp: str
    type: str


class PeerConnectionDescription(BaseModel):
    description: object
    pc_id: str
