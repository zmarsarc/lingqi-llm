from fastapi import FastAPI, Depends
from .model import SendPlainEmailRequest, CommonResponse
from .service import EmailService
from loguru import logger

app = FastAPI()


@app.post('/email/plain')
def send_plain_email(req: SendPlainEmailRequest, client: EmailService = Depends(EmailService)) -> CommonResponse:
    client.send_email(req.to, req.title, req.content)
    logger.info('send email <{}> to {}', req.title, req.to)
    return CommonResponse
