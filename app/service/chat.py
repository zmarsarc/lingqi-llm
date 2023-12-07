from fastapi import Depends
from app.service.db import database, Connection
from datetime import datetime
from typing import List
from app.model.chat import ChatHistoryRaw, LLMChatRequest, LLMChatResponse
from app.utilts import time
import httpx


class ChatHistoryService:
    """To manage use chat history."""

    def __init__(self, db: Connection = Depends(database)) -> None:
        self._db = db

    async def add_chat_log(self, uid: int, question: str, answer: str, qtime: datetime = None):
        if qtime is None:
            qtime = datetime.now()
        async with self._db.cursor() as cur:
            await cur.execute('insert into chat_history (user_id, question, answer, ctime) values (?, ?, ?, ?)',
                              (uid, question, answer, time.format_datetime(qtime)))
            await self._db.commit()

    async def get_user_chat_history(self, uid: int) -> List[ChatHistoryRaw]:
        async with self._db.execute('select * from chat_history where user_id = ?', (uid, )) as cur:
            cur.row_factory = ChatHistoryRaw.row_factory
            return await cur.fetchall()


url = "http://www.lingqi.tech:8606/chat/chat"


class ChatService:
    """Use to provide LLM chat service."""

    async def fastchat(self, content) -> LLMChatResponse:
        async with httpx.AsyncClient() as client:
            req = LLMChatRequest(query=content, conversation_id='test')

            # TODO set api timeout from config.
            resp = await client.post(url=url, json=req.model_dump(by_alias=True), timeout=15)
            return LLMChatResponse.model_validate_json(resp.content)