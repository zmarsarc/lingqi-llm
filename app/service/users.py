import sqlite3
from fastapi import Depends
from .db import database
from typing import List, Optional
from app.model.user import UserWithSecret
import random
import string
import hashlib
from app.utilts import time


class UserService:

    def __init__(self, conn: sqlite3.Connection = Depends(database)) -> None:
        self._conn = conn

    def insert_user(self, username: str, password: str) -> int:

        with self._conn:
            # Generate a random salt str.
            salt = ''.join(random.choices(
                string.ascii_lowercase + string.digits, k=8))

            # get encrypted password.
            pwd = self.gen_actual_pwd(password, salt)

            cur = self._conn.execute(
                'insert into users(username, password, salt, ctime) values (?, ?, ?, ?)', (username, pwd, salt, time.current_datetime_str()))
            return cur.lastrowid

    def get_all_users(self) -> List[UserWithSecret]:
        cur = self._conn.execute('select * from users;')
        res = []
        while True:
            ptr = cur.fetchone()
            if ptr is None:
                return res
            res.append(
                UserWithSecret(id=ptr['id'],
                               username=ptr['username'],
                               password=ptr['password'],
                               salt=ptr['salt'],
                               ctime=time.parse_daetetime(ptr['ctime'])))

    def find_user_by_name(self, username: str) -> Optional[UserWithSecret]:
        cur = self._conn.execute(
            'select * from users where username = ?', (username,))
        row = cur.fetchone()
        if row is None:
            return None
        return UserWithSecret(id=row['id'],
                              username=row['username'],
                              password=row['password'],
                              salt=row['salt'],
                              ctime=time.parse_daetetime(row['ctime']))

    def gen_actual_pwd(self, pwd: str, salt: str) -> str:
        return hashlib.sha1((pwd + salt).encode('ascii')).hexdigest()
