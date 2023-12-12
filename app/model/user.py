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

    @staticmethod
    def row_factory(cur, row):
        return UserWithSecret(
            id=row[0],
            username=row[1],
            password=row[2],
            salt=row[3],
            ctime=time.parse_datetime(row[4])
        )


class VerifiationRaw(BaseModel):
    id: int
    username: str
    code: str
    ctime: datetime
    ttl: int

    @staticmethod
    def row_factory(cur, row):
        return VerifiationRaw(
            id=row[0],
            username=row[1],
            code=row[2],
            ctime=time.parse_datetime(row[3]),
            ttl=row[4]
        )
