import logging
from sqlmodel import SQLModel, create_engine
from config.config import settings

log = logging.getLogger('uvicorn.debug')

engine = create_engine(settings.db_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    log.info("Database created")
