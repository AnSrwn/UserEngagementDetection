import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.database_service import DatabaseService
from network.routers import test
from network.routers import webrtc
from network.routers import engagement
from common.heartbeat import heartbeat

log = logging.getLogger("uvicorn.debug")

app = FastAPI(title="UserEngagementDetection")
log.info("FastAPI started")


# We define authorizations for middleware components
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# We use a callback to trigger the creation of the table if they don't exist yet
# When the API is starting
@app.on_event("startup")
def on_startup():
    with DatabaseService() as db_service:
        db_service.create_db_and_tables()
    # use heartbeat to test efficiency of multi-processing
    # asyncio.create_task(heartbeat())


app.include_router(test.router)
app.include_router(webrtc.router)
app.include_router(engagement.router)


@app.get("/")
async def root():
    return {"message": "UserEngagementDetection API is working."}
