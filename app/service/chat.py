import sqlite3
from fastapi import Depends
from app.service.db import database
from datetime import datetime
from typing import List, Any
from app.model.chat import ChatHistory
from pydantic import BaseModel
import httpx


class ChatHistoryService:
    """To manage use chat history."""

    def __init__(self, conn: sqlite3.Connection = Depends(database)) -> None:
        self._conn = conn

    def add_chat_log(self, uid: int, question: str, answer: str, qtime: datetime = None):
        if qtime is None:
            qtime = datetime.now()
        with self._conn:
            self._conn.execute('insert into chat_history (user_id, question, answer, ctime) values (?, ?, ?, ?)',
                               (uid, question, answer, qtime.strftime('%Y-%m-%d %H:%M:%S')))

    def get_user_chat_history(self, uid: int) -> List[ChatHistory]:
        cur = self._conn.execute(
            'select * from chat_history where user_id = ?', (uid, ))
        res = []
        for row in cur.fetchall():
            res.append(ChatHistory(id=row['id'], uid=row['user_id'], question=row['question'],
                       answer=row['answer'], time=datetime.strptime(row['ctime'], '%Y-%m-%d %H:%M:%S')))
        return res


class LLMFastChatRequest(BaseModel):

    class Message(BaseModel):
        role: str
        content: str

    model: str
    temperature: float
    n: int
    max_tokens: int
    stop: List[Any]
    stream: bool
    presence_penalty: int
    frequency_penalty: int
    messages: List[Message]


url = "http://www.lingqi.tech:8606/chat/fastchat"


class ChatService:
    """Use to provide LLM chat service."""

    async def fastchat(self, content) -> str:
        async with httpx.AsyncClient() as client:
            msg = LLMFastChatRequest.Message(role='user', content=content)
            req = LLMFastChatRequest(
                model="bc-wz-13bv5-8bits",
                temperature=0.7,
                n=1,
                max_tokens=0,
                stop=[],
                stream=False,
                presence_penalty=0,
                frequency_penalty=0,
                messages=[msg]
            )
            resp = await client.post(url=url, json=req.model_dump())
            print(resp.content)
            return resp.text
