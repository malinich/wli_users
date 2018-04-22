import asyncio
import hashlib
import uuid
from uuid import UUID

from tornado import gen

from .models import Users
from wli_users.apps.main.serializers import UserSchema
from wli_users.handlers import BaseHandler
from wli_users.utils import Router, validate_payload



@Router('/('
        '[0-9a-f]{8}-'
        '[0-9a-f]{4}-'
        '[0-9a-f]{4}-'
        '[0-9a-f]{4}-'
        '[0-9a-f]{12}$)'  # guid
        )
class UserHandler(BaseHandler):

    @gen.coroutine
    def get(self, guid):
        tramp = yield Users.find_one({"guid": UUID(guid)})
        self.write(Users.dump(tramp))


@Router('/', name="users-list")
class UsersHandler(BaseHandler):
    schema = UserSchema
    model = Users

    @gen.coroutine
    def get(self):
        self.render("templates/main.html")

    # @validate_payload(UserSchema)
    async def post(self, *args, **kwargs):
        payload = self.payload
        password = Users.create_password(payload.pop("password"))
        user = Users(**payload, password=password, guid=uuid.uuid4())
        files = await asyncio.ensure_future(
            self.upload_files(self.request.files.get("picture"), guid=user.guid))

        print(files)
        id_ = await user.commit()
        self.write(str(id_.inserted_id))

