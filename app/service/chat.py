import httpx
import functools
import re
from fastapi import Depends
from datetime import datetime
from typing import List, Dict
from app.service.db import database, Connection
from app.model.chat import ChatHistoryRaw, LLMChatRequest, LLMChatResponse
from app.utilts import time
from app.config import chat_settings


class LLMAPIError(Exception):
    pass

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

    async def get_user_chat_history_with_data_and_page(self, uid: int,
                                                       begin: datetime, end: datetime,
                                                       page: int, size: int
                                                       ) -> List[ChatHistoryRaw]:
        async with self._db.execute('select * from chat_history where user_id = ? and ctime between ? and ? order by id asc limit ? offset ?;',
                                    (uid, time.format_datetime(begin), time.format_datetime(end), size, page * size)) as cur:
            cur.row_factory = ChatHistoryRaw.row_factory
            return await cur.fetchall()

    async def list_conversation_calendar(self, uid: int) -> List[datetime]:
        async with self._db.execute('select distinct ctime from chat_history where user_id = ?', (uid,)) as cur:
            cur.row_factory = lambda _, r: time.parse_datetime(r[0])
            return await cur.fetchall()


class ChatService:
    """Use to provide LLM chat service."""

    def __init__(self, blacklist_path: str = chat_settings.blacklist_path) -> None:
        self._blacklist = self._load_blacklist(blacklist_path)

    async def chat(self, content) -> LLMChatResponse:
        async with httpx.AsyncClient() as client:
            req = LLMChatRequest(query=content, conversation_id='test')

            try:
                resp = await client.post(url=chat_settings.api_url, json=req.model_dump(by_alias=True), timeout=chat_settings.api_timeout)
            except httpx.TimeoutException:
                raise LLMAPIError("AI service busy, try later.")
            except httpx.HTTPError:
                raise LLMAPIError("AI service and temporary unusable, please try later.")
            return LLMChatResponse.model_validate_json(resp.content)

    def blacklist_check(self, content: str) -> bool:
        for p in self._blacklist.keys():
            if p.search(content):
                return False
        return True

    def blacklist_replace(self, content: str) -> str:
        res = content
        for p, r in self._blacklist.items():
            if p.search(content):
                res = re.sub(p, r, res)
        return res

    @functools.cache
    def _load_blacklist(self, path: str) -> Dict[re.Pattern, str]:
        res = {}
        try:
            with open(path, 'r') as fp:
                for line in fp.readlines():
                    word, replace = [x.strip() for x in line.split(':')]
                    res[re.compile(word)] = replace
        except FileNotFoundError:
            pass
        return res
