from sqlmodel import SQLModel, create_engine
from config.config import settings

engine = create_engine(settings.db_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
