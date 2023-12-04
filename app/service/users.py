import sqlite3
from pydantic import BaseModel
from fastapi import Depends
from .db import database
from typing import List, Optional
from app.model.user import User


class UserService:

    def __init__(self, conn: sqlite3.Connection = Depends(database)) -> None:
        self._conn = conn

    def insert_user(self, username: str, password: str) -> int:
        with self._conn:
            cur = self._conn.execute(
                'insert into users(username, password) values (?, ?)', (username, password))
            return cur.lastrowid

    def get_all_users(self) -> List[User]:
        cur = self._conn.execute('select * from users;')
        res = []
        while True:
            ptr = cur.fetchone()
            if ptr is None:
                return res
            res.append(
                User(id=ptr['id'], username=ptr['username'], password=ptr['password']))

    def find_user_by_name(self, username: str) -> Optional[User]:
        cur = self._conn.execute(
            'select * from users where username = ?', (username,))
        row = cur.fetchone()
        if row is None:
            return None
        return User(id=row['id'], username=row['username'], password=row['password'])
