from fastapi import Depends, Header, HTTPException
from app.service.users import UserService
from uuid import uuid4
from typing import Dict, Optional, Annotated
from app.model.auth import Session


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


sessions: Dict[str, Session] = {}
login_user_token: Dict[int, str] = {}


class AuthService:

    def __init__(self, srv: UserService = Depends(UserService)) -> None:
        self._srv = srv

    def login(self, username: str, password: str) -> str:
        user = self._srv.find_user_by_name(username)
        if user is None:
            raise UserNotExistsError(username=username)
        if user.password != self._srv.gen_actual_pwd(password, user.salt):
            raise PasswordIncorrectError(username, password)

        # If user already logined, return same token.
        if user.id in login_user_token:
            return login_user_token[user.id]

        # Or make a new token.
        token = str(uuid4())
        sessions[token] = Session(token=token, user=user)
        login_user_token[user.id] = token
        return token

    def get_session_by_token(self, token: str) -> Optional[Session]:
        return sessions.get(token)


def check_valid_auth(authorization: Annotated[str, Header()], auth: AuthService = Depends(AuthService)):
    scheme, credential = authorization.split()
    if scheme.lower() != 'bearer':
        raise HTTPException(
            status_code=401, detail="authorization scheme not support.")

    ses = auth.get_session_by_token(credential)
    if ses is None:
        raise HTTPException(status_code=401, detail="need login.")
    return ses
