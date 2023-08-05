from pydantic import BaseModel


class OfferRequest(BaseModel):
    sdp: str
    type: str
