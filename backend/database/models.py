from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional

class Test(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    isSuper: bool
    