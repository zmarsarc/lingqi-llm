from pydantic import BaseModel, field_serializer, Field
from datetime import datetime
from app.utilts import time
from enum import Enum
from typing import List


class ChatHistoryContent(BaseModel):
    question: str
    answer: str
    time: datetime

    @field_serializer('time')
    def format_time(self, dt: datetime):
        return time.format_datetime(dt)


class ChatHistoryRaw(ChatHistoryContent):
    id: int
    uid: int

    @staticmethod
    def row_factory(cur, row):
        return ChatHistoryRaw(
            id=row[0],
            uid=row[1],
            question=row[2],
            answer=row[3],
            time=time.parse_datetime(row[4])
        )


class ChatRole(str, Enum):
    User = 'user'
    Assistant = 'assistant'


class ChatMessage(BaseModel):
    role: str
    content: str


class LLMChatRequest(BaseModel):
    query: str
    conversation_id: str
    history_len: int = Field(default=-1)
    history: List[ChatMessage] = []
    stream: bool = False
    llm_model_name: str = Field(
        default="bc-wz-13bv3-8bits", alias='model_name')
    temperature: float = 0.4
    max_tokens: int = 0
    propmt_name: str = "default"


class LLMChatResponse(BaseModel):
    text: str
    message_id: str
