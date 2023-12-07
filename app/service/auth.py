from fastapi import Depends, Header, HTTPException
import base64
from loguru import logger
from uuid import uuid4
from typing import Annotated
from datetime import datetime
from app.service.users import UserService
from app.service.db import session_database, Connection
from app.model.user import UserBasic
from app.model.auth import Session, SessionRaw
from app.config import auth_settings
from app.utilts.time import format_datetime


class LoginError(Exception):
    pass


class UserNotExistsError(LoginError):
    def __init__(self, username: str, *args: object) -> None:
        super().__init__(*args)
        self.username = username


class PasswordIncorrectError(LoginError):
    def __init__(self, username: str, pwd: str, *args: object) -> None:
        super().__init__(*args)
        self.username = username
        self.pwd = pwd


class SessionNotExistsError(Exception):
    def __init__(self, uid: int, *args: object) -> None:
        super().__init__(*args)
        self.uid = uid


class SessionManager:

    def __init__(self, db: Connection = Depends(session_database),
                 users: UserService = Depends(UserService)) -> None:
        self._db = db
        self._users = users

    async def new_session(self, user: UserBasic, dt: datetime, expires: int) -> Session:
        token = str(uuid4())
        async with self._db.cursor() as cur:
            await cur.execute('insert into sessions (uid, token, ctime, utime, expires)values (?, ?, ?, ?, ?)', (
                user.id, token,
                format_datetime(dt), format_datetime(dt), expires
            ))
            await self._db.commit()
        return Session(token=token, user=user, login_time=dt,
                       update_time=dt, expires=expires)

    async def find_session_by_uid(self, uid: int) -> Session | None:
        async with self._db.execute('select * from sessions where uid = ?', (uid, )) as cur:
            cur.row_factory = SessionRaw.row_factory
            ses: SessionRaw = await cur.fetchone()
        if ses is None:
            return None

        user = await self._users.get(ses.uid)
        if user is None:
            return user

        return Session(token=ses.token, user=user, login_time=ses.ctime, update_time=ses.utime, expires=ses.expires)

    async def find_session_by_token(self, tk: str) -> Session | None:
        async with self._db.execute('select * from sessions where token = ?', (tk, )) as cur:
            cur.row_factory = SessionRaw.row_factory
            ses: SessionRaw = await cur.fetchone()
        if ses is None:
            return None

        user = await self._users.get(ses.uid)
        if user is None:
            return user

        return Session(token=ses.token, user=user, login_time=ses.ctime, update_time=ses.utime, expires=ses.expires)

    async def flush_session(self, dt: datetime, uid: int):
        async with self._db.cursor() as cur:
            cur = await cur.execute('update sessions set utime = ? where uid = ?', (format_datetime(dt), uid))
            if cur.rowcount == 0:
                raise SessionNotExistsError(uid)


class AuthService:

    def __init__(self,
                 users: UserService = Depends(UserService),
                 sessions: SessionManager = Depends(SessionManager)) -> None:
        self._users = users
        self._sessions = sessions

    async def login(self, username: str, password: str) -> Session:
        user = await self._users.find_user_by_name(username)
        if user is None:
            raise UserNotExistsError(username=username)
        if user.password != self._users.gen_actual_pwd(password, user.salt):
            raise PasswordIncorrectError(username, password)

        # If user already logined, return same token.
        ses = await self._sessions.find_session_by_uid(user.id)
        if ses is not None:
            await self._sessions.flush_session(datetime.now(), ses.user.id)
            return ses

        # Or make a new token.
        ses = await self._sessions.new_session(user, datetime.now(), auth_settings.expires)
        logger.info("user login, ses: {}, username: {}", ses.token, username)
        return ses


async def valid_session(authorization: Annotated[str, Header()],
                        auth: AuthService = Depends(AuthService),
                        sessions: SessionManager = Depends(SessionManager)) -> Session:
    scheme, credential = authorization.split()

    if scheme.lower() == 'bearer':
        ses = await sessions.find_session_by_token(credential)
        if ses is None:
            raise HTTPException(status_code=401, detail="need login.")
        await sessions.flush_session(datetime.now(), ses.user.id)
        return ses

    if scheme.lower() == 'basic':
        raw = base64.b64decode(credential).decode('ascii')
        username, password = raw.split(':')
        try:
            ses = await auth.login(username=username, password=password)
        except LoginError:
            raise HTTPException(401, "incorrect username or password.")
        return ses

    raise HTTPException(401, "authorization scheme not support.")
