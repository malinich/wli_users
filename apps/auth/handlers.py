import json

import jwt

from wli_users.handlers import BaseHandler
from wli_users.settings import SECRET_KEY
from wli_users.utils import Routers
from ..main.models import Users


@Routers("/auth")
class AuthHandler(BaseHandler):
    schema = Users

    async def post(self):
        data = json.loads(self.request.body)
        try:
            email = data["email"]
            password = data["password"]
        except:
            self.set_status(403)
            return

        if password:
            hash_password = Users.create_password(password.encode('utf-8'))
            result = await self.schema.find_one({"email": email, "password": hash_password})

        if result is not None and result.pk is not None:
            dataToken = {"guid": str(result.guid), "email": result.email}
            token = jwt.encode(dataToken, SECRET_KEY, algorithm='HS256')
            status = True
            res = result.email
        else:
            token = None
            status = False
            res = "Invalid Username or Password."

        self.write({"data": res, "result": status, "token": token.decode("utf-8")})
        self.finish()
