import httpx
from app.config import app_settings


class EmailProxy:

    async def send_plain_email(self, to: str, title: str, content: str):
        endpoing = app_settings.email_proxy_url + '/email/plain'
        async with httpx.AsyncClient(verify=False) as client:
            await client.post(url=endpoing, json={
                'to': to, 'title': title, 'content': content
            })
