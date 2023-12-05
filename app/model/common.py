from pydantic import BaseModel


class CommonResponse(BaseModel):
    code: int = 0
    msg: str = 'ok'
