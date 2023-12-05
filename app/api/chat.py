from fastapi import APIRouter, Depends
from app.service.auth import check_valid_auth
from app.model.auth import Session
from pydantic import BaseModel
from app.service.chat import ChatService
from app.model.common import CommonResponse

router = APIRouter()


@router.get('/history')
async def get_chat_history(ses: Session = Depends(check_valid_auth), srv: ChatService = Depends(ChatService)):
    return srv.get_user_chat_history(ses.user.id)


class ChatRequest(BaseModel):
    question: str


class ChatResponse(CommonResponse):
    answer: str


@router.post('/chat')
async def chat(req: ChatRequest, ses: Session = Depends(check_valid_auth), srv: ChatService = Depends(ChatService)) -> ChatResponse:

    # TODO get answer from LLV via http API.
    answer = req.question
    srv.add_chat_log(ses.user.id, req.question, answer)
    return ChatResponse(answer=answer)
