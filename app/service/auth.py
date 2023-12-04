from fastapi import Depends
from app.service.users import UserService, User
from uuid import uuid4
from typing import Dict


class LoginError(Exception):
    pass


class UserNotExistsError(LoginError):
    def __init__(self, username: str, *args: object) -> None:
        super().__init__(*args)
        self.username = username


class PasswordIncorrectError(LoginError):
    def __init__(self, username: str, correct_pwd: str, actual_pwd: str, *args: object) -> None:
        super().__init__(*args)
        self.username = username
        self.pwd = correct_pwd
        self.actual = actual_pwd


session: Dict[str, User] = {}
login_user_token: Dict[int, str] = {}


class AuthService:

    def __init__(self, srv: UserService = Depends(UserService)) -> None:
        self._srv = srv

    def login(self, username: str, password: str) -> str:
        user = self._srv.find_user_by_name(username)
        if user is None:
            raise UserNotExistsError(username=username)
        if user.password != password:
            raise PasswordIncorrectError(username, user.password, password)

        # If user already logined, return same token.
        if user.id in login_user_token:
            return login_user_token[user.id]

        # Or make a new token.
        token = str(uuid4())
        session[token] = user
        login_user_token[user.id] = token
        return token
