from fastapi import APIRouter, Depends
from typing import List
from pydantic import BaseModel
from loguru import logger
from app.service.auth import valid_session
from app.model.auth import Session
from app.service.chat import ChatHistoryService, ChatService
from app.model.common import CommonResponse
from app.model.chat import ChatHistoryRaw
from app.config import chat_settings

router = APIRouter()


@router.get('/history')
async def get_chat_history(ses: Session = Depends(valid_session), srv: ChatHistoryService = Depends(ChatHistoryService)) -> List[ChatHistoryRaw]:
    return await srv.get_user_chat_history(ses.user.id)


class ChatRequest(BaseModel):
    question: str


class ChatResponse(CommonResponse):
    answer: str


# TODO add filter in this API.
@router.post('/chat')
async def chat(req: ChatRequest, ses: Session = Depends(valid_session),
               history: ChatHistoryService = Depends(ChatHistoryService),
               chat: ChatService = Depends(ChatService)) -> ChatResponse:

    # Do not check blacklist check, just ask.
    if chat_settings.blacklist_mode == chat_settings.BlacklistMode.Disable:
        answer = await chat.chat(req.question)
        await history.add_chat_log(ses.user.id, req.question, answer.text)
        return ChatResponse(answer=answer.text)

    # Block any content include words in blacklist.
    if chat_settings.blacklist_mode == chat_settings.BlacklistMode.Block:
        if not chat.blacklist_check(req.question):
            logger.info(
                "user content include senstive content, it will be blocked. content is \"{}\"", req.question)
            return ChatResponse(answer=chat_settings.blacklist_block_hint)

        answer = await chat.chat(req.question)
        if not chat.blacklist_check(answer.text):
            logger.info(
                'assistant content include senstive content, it will be blocked. content is \"{}\"', answer.text)
            return ChatResponse(answer=chat_settings.blacklist_block_hint)

        await history.add_chat_log(ses.user.id, req.question, answer.text)
        return ChatResponse(answer=answer.text)

    # Replace those words in blacklist by safe words.
    if chat_settings.blacklist_mode == chat_settings.BlacklistMode.Replace:
        answer = await chat.chat(req.question)
        safe_question = chat.blacklist_replace(req.question)
        safe_answer = chat.blacklist_replace(answer.text)
        await history.add_chat_log(ses.user.id, safe_question, safe_answer)
        return ChatResponse(answer=safe_answer)
