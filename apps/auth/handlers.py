import json

import jwt

from wli_users.handlers import BaseHandler


class AuthHandler(BaseHandler):
    def post(self):
        data = json.loads(self.request.body)
        try:
            login = data["username"]
            password = data["password"]
        except:
            self.set_status(403)
            return

        if password:
            query = "SELECT id, login FROM user WHERE login = %s AND password = SHA1(%s)"
            result = self.db.get(query, login, password)

        if result is not None and result.id is not None:
            dataToken = {"id": result.id, "login": result.login}
            token = jwt.encode(dataToken, "nyxjs", algorithm='HS256')
            status = True
            res = result
        else:
            token = None
            status = False
            res = "Invalid Username or Password."

        self.write({"data": res, "result": status, "token": token})
        self.finish()
