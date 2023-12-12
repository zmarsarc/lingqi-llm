from fastapi import Depends
from .db import database, session_database, Connection
from aiosqlite import IntegrityError
from typing import List, Optional
from app.model.user import UserWithSecret, VerifiationRaw
import random
import string
import hashlib
from app.utilts import time
from datetime import datetime


class UserAlreadyExistsError(Exception):
    pass


class UserService:

    def __init__(self, db: Connection = Depends(database)) -> None:
        self._db = db

    async def insert_user(self, username: str, password: str) -> int:
        random.seed(datetime.now().timestamp())

        # Generate a random salt str.
        salt = ''.join(random.choices(
            string.ascii_lowercase + string.digits, k=8))

        # get encrypted password.
        pwd = self.gen_actual_pwd(password, salt)

        try:
            async with self._db.cursor() as cur:
                cur = await cur.execute(
                    'insert into users(username, password, salt, ctime) values (?, ?, ?, ?)', (username, pwd, salt, time.current_datetime_str()))
                await self._db.commit()
                return cur.lastrowid
        except IntegrityError:
            raise UserAlreadyExistsError(
                'username \"{}\" alerady in used.'.format(username))

    async def get_all_users(self) -> List[UserWithSecret]:
        async with self._db.execute('select * from users;') as cur:
            cur.row_factory = UserWithSecret.row_factory
            return await cur.fetchall()

    async def find_user_by_name(self, username: str) -> Optional[UserWithSecret]:
        async with self._db.execute('select * from users where username = ?', (username,)) as cur:
            cur.row_factory = UserWithSecret.row_factory
            return await cur.fetchone()

    async def get(self, uid: int) -> UserWithSecret | None:
        async with self._db.execute('select * from users where id = ?', (uid, )) as cur:
            cur.row_factory = UserWithSecret.row_factory
            return await cur.fetchone()

    def gen_actual_pwd(self, pwd: str, salt: str) -> str:
        return hashlib.sha1((pwd + salt).encode('ascii')).hexdigest()


class VerifiationService:

    def __init__(self, db: Connection = Depends(session_database)) -> None:
        self._db = db

    async def gen_verifiation_code(self, username: str, ttl: int) -> str:
        random.seed(datetime.now().timestamp())
        code = ''.join(random.choices(string.digits, k=6))
        async with self._db.cursor() as cur:
            await cur.execute('select count(*) from verifiations where username = ?', (username, ))
            cnt = (await cur.fetchone())[0]
            if cnt == 0:
                await cur.execute('insert into verifiations(username, code, ctime, ttl) values (?, ?, ?, ?)',
                                  (username, code, time.format_datetime(datetime.now()), ttl))
            else:
                await cur.execute('update verifiations set code = ?, ctime = ?, ttl = ? where username = ?', (
                    code, time.format_datetime(datetime.now()), ttl, username
                ))
            await self._db.commit()
        return code

    async def get(self, username: str) -> VerifiationRaw | None:
        async with self._db.execute('select * from verifiations where username = ?', (username,)) as cur:
            cur.row_factory = VerifiationRaw.row_factory
            return await cur.fetchone()
