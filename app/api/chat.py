from fastapi import APIRouter, Depends
from app.service.auth import valid_session
from app.model.auth import Session
from pydantic import BaseModel
from app.service.chat import ChatHistoryService, ChatService
from app.model.common import CommonResponse
from typing import List
from app.model.chat import ChatHistoryRaw

router = APIRouter()


@router.get('/history')
async def get_chat_history(ses: Session = Depends(valid_session), srv: ChatHistoryService = Depends(ChatHistoryService)) -> List[ChatHistoryRaw]:
    return await srv.get_user_chat_history(ses.user.id)


class ChatRequest(BaseModel):
    question: str


class ChatResponse(CommonResponse):
    answer: str


@router.post('/chat')
async def chat(req: ChatRequest, ses: Session = Depends(valid_session),
               history: ChatHistoryService = Depends(ChatHistoryService),
               chat: ChatService = Depends(ChatService)) -> ChatResponse:

    answer = await chat.fastchat(req.question)
    await history.add_chat_log(ses.user.id, req.question, answer.text)
    return ChatResponse(answer=answer.text)
