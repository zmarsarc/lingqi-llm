from pydantic import BaseModel


class CommonResponse(BaseModel):
    code: int = 0
    msg: str = 'ok'


class SendPlainEmailRequest(BaseModel):
    to: str
    title: str
    content: str
