from pydantic import BaseModel


class SendPlainEmailRequest(BaseModel):
    to: str
    title: str
    content: str
