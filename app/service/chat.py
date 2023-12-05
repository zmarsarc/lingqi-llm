import sqlite3
from fastapi import Depends
from app.service.db import database
from datetime import datetime
from typing import List
from app.model.chat import ChatHistory


class ChatService:

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
