import smtplib
import email.message
from .config import msg_settings, msg_secrets


class EmailService:

    def send_email(self, to: str, title: str, content: str):
        msg = email.message.EmailMessage()
        msg['Subject'] = title
        msg['From'] = msg_secrets.smtp_username
        msg['To'] = to
        msg.set_content(content)

        with smtplib.SMTP_SSL(msg_settings.smtp_host) as client:
            client.login(msg_secrets.smtp_username, msg_secrets.smtp_password)
            return client.send_message(msg)
            
