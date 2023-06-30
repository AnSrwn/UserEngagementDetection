from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional


def to_camel_case(snake_str):
    return "".join(x.capitalize() for x in snake_str.lower().split("_"))


def to_camel(snake_str):
    # We capitalize the first letter of each component except the first one
    # with the 'capitalize' method and join them together.
    camel_string = to_camel_case(snake_str)
    return snake_str[0].lower() + camel_string[1:]


class BaseModel(SQLModel):
    """Base SQL model class."""

    id: Optional[int] = Field(default=None, primary_key=True)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


#  TODO: remove test
class Test(BaseModel, table=True):
    """Test table."""

    name: str
    is_super: bool


class Engagement(BaseModel, table=True):
    """Engagement table."""

    peer_connection: str
    time: datetime
    boredom: float
    engagement: float
    confusion: float
    frustration: float
