from pydantic import BaseModel


class Responses(BaseModel):
    code: int = 0
    msg: str = 'ok'
