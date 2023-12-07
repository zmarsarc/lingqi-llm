from fastapi import APIRouter, Depends
from app.service.users import UserService
from app.model.user import UserBasic
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
async def add_user(user: AddUserRequest, srv: UserService = Depends(UserService)) -> AddUserResponse:
    id = await srv.insert_user(user.username, user.password)
    return AddUserResponse(username=user.username, id=id)


@router.get('/users')
async def list_users(srv: UserService = Depends(UserService)) -> List[UserBasic]:
    return await srv.get_all_users()
