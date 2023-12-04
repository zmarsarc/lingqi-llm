from fastapi import APIRouter

router = APIRouter()

@router.post('/user')
async def add_user():
    return {"message": "Add User"}