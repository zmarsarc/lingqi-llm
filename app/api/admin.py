from fastapi import APIRouter, Depends
from app.service.users import UserService
from app.model.user import User
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
    id = srv.insert_user(user.username, user.password)
    return AddUserResponse(username=user.username, id=id)


@router.get('/users')
async def list_users(srv: UserService = Depends(UserService)) -> List[User]:
    return srv.get_all_users()
