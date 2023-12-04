from fastapi import APIRouter

router = APIRouter()

@router.get('/history')
async def get_chat_history():
    return {"message": "Chat History"}

@router.post('/chat')
async def chat():
    return {"meddage": "Chat"}