from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.service.auth import AuthService, LoginError

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    code: int = 0
    msg: str = 'ok'
    token: str


@router.post('/login')
async def login(req: LoginRequest, auth_srv: AuthService = Depends(AuthService)) -> LoginResponse:
    try:
        token = auth_srv.login(req.username, req.password)
        return LoginResponse(token=token)
    except LoginError:
        return LoginResponse(code=1, msg="username or password incorrect.", token='')