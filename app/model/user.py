from pydantic import BaseModel, Field, field_serializer
from datetime import datetime
from app.utilts import time


class UserBasic(BaseModel):
    id: int
    username: str
    ctime: datetime

    @field_serializer('ctime')
    def parse_time(self, dt: datetime):
        return time.format_datetime(dt)


class UserWithSecret(UserBasic):
    password: str = Field(exclude=True)
    salt: str = Field(exclude=True)
