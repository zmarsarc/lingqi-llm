from pydantic import BaseModel, Field
from . import user
from datetime import datetime


class Session(BaseModel):
    token: str
    user: user.UserBasic
    login_time: datetime = Field(default_factory=datetime.now)
