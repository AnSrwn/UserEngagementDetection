from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database.models import Test
from database.database import engine, create_db_and_tables
from routers import test

app = FastAPI(title="UserEngagementDetection")


#We define authorizations for middleware components
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
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
