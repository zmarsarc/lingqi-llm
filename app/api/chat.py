from fastapi import APIRouter, Depends, Query, UploadFile
from typing import List
from pydantic import BaseModel, field_serializer
from loguru import logger
from datetime import datetime, timedelta
from app.service.auth import valid_session
from app.model.auth import Session
from app.service.chat import ChatHistoryService, ChatService, LLMAPIError
from app.model.common import CommonResponse
from app.model.chat import ChatHistoryContent
from app.config import chat_settings
from app.utilts.time import parse_date, format_date

router = APIRouter()


class GetChatHistoryResponse(CommonResponse):
    total: int
    history: List[ChatHistoryContent]


@router.get('/history')
async def get_chat_history(
        start: str = Query(pattern='^\d{4}-\d{2}-\d{2}$'),
        end: str = Query(pattern='^\d{4}-\d{2}-\d{2}$'),
        page: int = Query(ge=0),
        size: int = Query(ge=1),
        ses: Session = Depends(valid_session),
        srv: ChatHistoryService = Depends(ChatHistoryService)
) -> GetChatHistoryResponse | CommonResponse:

    try:
        start_time = parse_date(start)
        end_time = parse_date(end)
    except ValueError:
        return CommonResponse(code=1, msg="invalid data format, data should list yyyy-mm-dd")
    cnt, res = await srv.get_user_chat_history_with_data_and_page(ses.user.id, start_time, end_time, page - 1, size)
    return GetChatHistoryResponse(history=res, total=cnt)


class GetChatHistoryTodayResponse(GetChatHistoryResponse):
    today: datetime

    @field_serializer('today')
    def format_today(self, dt: datetime):
        return format_date(dt)


@router.get('/history/today')
async def get_chat_history_in_today(
    page: int = Query(ge=0),
    size: int = Query(ge=1),
    ses: Session = Depends(valid_session),
    srv: ChatHistoryService = Depends(ChatHistoryService)
) -> GetChatHistoryTodayResponse | CommonResponse:
    cur = datetime.now()
    start_time = datetime(cur.year, cur.month, cur.day)
    end_time = start_time + timedelta(days=1)

    cnt, res = await srv.get_user_chat_history_with_data_and_page(ses.user.id, start_time, end_time, page - 1, size)
    return GetChatHistoryTodayResponse(total=cnt, history=res, today=start_time)


class GetChatHistoryCalendarResponse(CommonResponse):
    data: List[datetime]

    @field_serializer('data')
    def format_data(self, dt: List[datetime]):
        return list(dict.fromkeys([format_date(x) for x in dt]))


@router.get('/history/calendar')
async def get_chat_history_calendar(
    ses: Session = Depends(valid_session),
    srv: ChatHistoryService = Depends(ChatHistoryService)
) -> GetChatHistoryCalendarResponse:
    res = await srv.list_conversation_calendar(ses.user.id)
    return GetChatHistoryCalendarResponse(data=res)


class ChatRequest(BaseModel):
    question: str


class ChatResponse(CommonResponse):
    answer: str


@router.post('/chat')
async def chat(req: ChatRequest, ses: Session = Depends(valid_session),
               history: ChatHistoryService = Depends(ChatHistoryService),
               chat: ChatService = Depends(ChatService)) -> ChatResponse | CommonResponse:

    try:
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
    except LLMAPIError as e:
        return CommonResponse(code=1, msg=str(e))


class AutomaticSpeechRecognizationResponse(CommonResponse):
    text: str


@router.post('/chat/asr')
async def automatic_speech_recognize(file: UploadFile, ses: Session = Depends(valid_session), chat: ChatService = Depends(ChatService)):
    res = await chat.asr(file)
    return AutomaticSpeechRecognizationResponse(text=res)
