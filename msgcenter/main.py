from fastapi import FastAPI, Depends
from .model import SendPlainEmailRequest
from .service import EmailService
from loguru import logger
import smtplib
from responses import Responses, msgcenter

app = FastAPI()


@app.post('/email/plain')
def send_plain_email(req: SendPlainEmailRequest, client: EmailService = Depends(EmailService)) -> Responses:
    try:
        client.send_email(req.to, req.title, req.content)
    except smtplib.SMTPRecipientsRefused:
        logger.error('email rejected. no such address or access denied.')
        return msgcenter.email_recipients_refused

    logger.info('send email <{}> to {}', req.title, req.to)
    return Responses()
