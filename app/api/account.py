from fastapi import APIRouter, Depends
from pydantic import BaseModel
from loguru import logger
from datetime import datetime, timedelta
from app.model.common import CommonResponse
from app.service.users import UserService, VerifiationService
from app.config import auth_settings

router = APIRouter()


class PrepareRegisterRequest(BaseModel):
    username: str


class PrepareRegisterResponse(CommonResponse):
    ttl: int


@router.post('/register/prepare')
async def prepare_register(req: PrepareRegisterRequest,
                           users: UserService = Depends(UserService),
                           verifiation: VerifiationService = Depends(
                               VerifiationService)
                           ) -> PrepareRegisterResponse | CommonResponse:
    u = await users.find_user_by_name(req.username)
    if u is not None:
        return CommonResponse(code=1, msg="username already in used.")
    code = await verifiation.gen_verifiation_code(req.username, auth_settings.verifiation_ttl)
    logger.info('"{}" prepare to register, code {}', req.username, code)
    return PrepareRegisterResponse(ttl=auth_settings.verifiation_ttl)


class RegisterRequest(BaseModel):
    username: str
    password: str
    code: str


@router.post('/register/apply')
async def apply_register(req: RegisterRequest,
                         users: UserService = Depends(UserService),
                         verifiation: VerifiationService = Depends(
                             VerifiationService)
                         ) -> CommonResponse:
    if (await users.find_user_by_name(req.username)) is not None:
        return CommonResponse(code=1, msg="username already in used.")

    ticket = await verifiation.get(req.username)
    if ticket is None or (ticket.ctime + timedelta(seconds=ticket.ttl)) < datetime.now():
        return CommonResponse(code=2, msg="verification code expired or no such code.")

    if ticket.code != req.code:
        return CommonResponse(code=3, msg="verification code incorrect.")

    await users.insert_user(req.username, req.password)
    return CommonResponse()
