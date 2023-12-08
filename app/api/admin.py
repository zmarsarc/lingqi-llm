from fastapi import APIRouter, Depends
from app.service.users import UserService, UserAlreadyExistsError
from app.model.user import UserBasic
from app.model.common import CommonResponse
from typing import List
from pydantic import BaseModel

router = APIRouter()


class AddUserRequest(BaseModel):
    username: str
    password: str


class AddUserResponse(BaseModel):
    username: str
    id: int


@router.post('/user')
async def add_user(user: AddUserRequest, srv: UserService = Depends(UserService)) -> AddUserResponse | CommonResponse:
    try:
        id = await srv.insert_user(user.username, user.password)
        return AddUserResponse(username=user.username, id=id)
    except UserAlreadyExistsError as e:
        return CommonResponse(code=1, msg=str(e))


@router.get('/users')
async def list_users(srv: UserService = Depends(UserService)) -> List[UserBasic]:
    return await srv.get_all_users()
