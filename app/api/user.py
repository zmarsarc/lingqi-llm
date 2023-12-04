from fastapi import APIRouter

router = APIRouter()

@router.get('/config')
async def get_user_config():
    return {"message": "User Config"}

@router.post('/config')
async def set_user_config():
    return {"message": "Set User Config"}