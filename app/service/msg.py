import httpx
from http.client import responses
from app.config import app_settings
from responses import Responses


class ProxyError(Exception):
    pass


class EmailProxy:

    async def send_plain_email(self, to: str, title: str, content: str) -> Responses:
        endpoing = app_settings.email_proxy_url + '/email/plain'
        async with httpx.AsyncClient(verify=False) as client:
            resp = await client.post(url=endpoing, json={
                'to': to, 'title': title, 'content': content
            })
            if resp.status_code != 200:
                raise ProxyError('call internal API error, <{} {}>'.format(
                                 resp.status_code, responses[resp.status_code]))
            return Responses.model_validate_json(resp.text)
