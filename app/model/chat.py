from pydantic import BaseModel
from datetime import datetime


class ChatHistory(BaseModel):
    id: int
    uid: int
    question: str
    answer: str
    time: datetime
