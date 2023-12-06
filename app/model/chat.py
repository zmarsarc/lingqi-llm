from pydantic import BaseModel, field_serializer
from datetime import datetime
from app.utilts import time


class ChatHistory(BaseModel):
    id: int
    uid: int
    question: str
    answer: str
    time: datetime

    @field_serializer('time')
    def format_time(self, dt: datetime):
        return time.format_datetime(dt)