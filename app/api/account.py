from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from loguru import logger
from datetime import datetime, timedelta
from responses import Responses, internal_error, ok
from app.service.users import UserService, VerifiationService
from app.service.msg import EmailProxy, ProxyError
from app.config import auth_settings

router = APIRouter()


class PrepareRegisterRequest(BaseModel):
    username: EmailStr


class PrepareRegisterResponse(Responses):
    ttl: int


@router.post('/register/prepare')
async def prepare_register(req: PrepareRegisterRequest,
                           users: UserService = Depends(UserService),
                           verifiation: VerifiationService = Depends(
                               VerifiationService),
                           proxy: EmailProxy = Depends(EmailProxy)
                           ) -> PrepareRegisterResponse | Responses:
    u = await users.find_user_by_name(req.username)
    if u is not None:
        return ResourceWarning(code=1, msg="username already in used.")
    code = await verifiation.gen_verifiation_code(req.username, auth_settings.verifiation_ttl)
    logger.info('"{}" prepare to register, code {}', req.username, code)

    try:
        resp = await proxy.send_plain_email(req.username, 'Register Verfication Code', 'Your verification code is {}.'.format(code))
        if resp.code != ok.code:
            return resp
    except ProxyError as e:
        logger.error('error when send verification email, {}', str(e))
        return internal_error

    return PrepareRegisterResponse(ttl=auth_settings.verifiation_ttl)


class RegisterRequest(BaseModel):
    username: EmailStr
    password: str
    code: str


@router.post('/register/apply')
async def apply_register(req: RegisterRequest,
                         users: UserService = Depends(UserService),
                         verifiation: VerifiationService = Depends(
                             VerifiationService)
                         ) -> Responses:
    if (await users.find_user_by_name(req.username)) is not None:
        return Responses(code=1, msg="username already in used.")

    ticket = await verifiation.get(req.username)
    if ticket is None or (ticket.ctime + timedelta(seconds=ticket.ttl)) < datetime.now():
        return Responses(code=2, msg="verification code expired or no such code.")

    if ticket.code != req.code:
        return Responses(code=3, msg="verification code incorrect.")

    await users.insert_user(req.username, req.password)
    return Responses()
