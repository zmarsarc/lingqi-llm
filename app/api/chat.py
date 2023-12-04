from fastapi import APIRouter, Depends
from app.service.auth import check_valid_auth
from app.model.auth import Session

router = APIRouter()

@router.get('/history')
async def get_chat_history(ses: Session = Depends(check_valid_auth)):
    return {"message": "Chat History"}

@router.post('/chat')
async def chat(ses: Session = Depends(check_valid_auth)):
    return {"meddage": "Chat"}