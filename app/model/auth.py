from pydantic import BaseModel
from . import user
from datetime import datetime
from app.utilts.time import parse_datetime


class SessionRaw(BaseModel):
    uid: int
    token: str
    ctime: datetime
    utime: datetime
    expires: int

    @staticmethod
    def row_factory(cur, row):
        return SessionRaw(
            uid=row[0],
            token=row[1],
            ctime=parse_datetime(row[2]),
            utime=parse_datetime(row[3]),
            expires=row[4]
        )


class Session(BaseModel):
    token: str
    user: user.UserBasic
    login_time: datetime
    update_time: datetime
    expires: int
