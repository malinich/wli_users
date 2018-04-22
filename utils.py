import json
from typing import Type

import tornado.web
from marshmallow import Schema


class Routers:
    _routes = []

    def __init__(self, url, name=None):
        self._url = url
        self.name = name

    def __call__(self, handler):
        name = self.name or handler.__name__
        self._routes.append(tornado.web.url(self._url, handler, name=name))

    @classmethod
    def get_routes(cls):
        return cls._routes


def validate_payload(schema: Type[Schema]):
    def decor(func):
        async def wrap(self: tornado.web.RequestHandler, *args, **kwargs):
            row_data = self.payload
            json_data = \
                {k: v[0] if len(v) <= 1 else v for k, v in row_data.items()}
            errors = schema(json_data).validate(json_data)
            if errors:
                return self.send_error(400, reason=json.dumps(errors))
            res = func(self, *args, **kwargs)
            return await res

        return wrap

    return decor
