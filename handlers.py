import asyncio
import uuid
from pprint import pprint

import aiohttp
import traceback

import jwt
import tornado.web
from aiohttp import FormData

from wli_users import settings
from wli_users.settings import SECRET_KEY


class BaseHandler(tornado.web.RequestHandler):

    def get_current_user(self):
        x_auth_token = self.request.headers.get("Auth-Token")
        data = jwt.decode(x_auth_token, SECRET_KEY, algorithms="HS256")
        return data.get('guid')

    @property
    def db(self):
        return self.application.db

    @property
    def db_instance(self):
        return self.application.db_instance

    @property
    def payload(self) -> dict:
        body_data = self.request.body_arguments
        data = \
            {k: v[0] if len(v) <= 1 else v for k, v in body_data.items()}
        return data

    async def upload_files(self, files, guid):
        async with self.get_session() as session:
            data = FormData()
            data.add_field('data',
                           files[0]['body'],
                           filename=files[0]['filename'], )
            data.add_field("user", str(guid))
            res = await session.post(settings.upload_service, data=data)
        # tasks = [asyncio.Task(aiohttp.request("POST", settings.upload_service, data=f)) for f in files]
        # res = await asyncio.gather(*tasks)
        return res

    def write_error(self, status_code, **kwargs):
        self.set_header("Content-Type", "application/json")

        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            self.set_header('Content-Type', 'text/plain')
            for line in traceback.format_exception(*kwargs["exc_info"]):
                self.write(line)
            self.finish()
        else:
            self.finish({
                "code": status_code,
                "message": self._reason,
            })

    def get_session(self):
        return aiohttp.ClientSession()
