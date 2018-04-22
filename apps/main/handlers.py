import asyncio
import hashlib
import uuid
from uuid import UUID

from tornado import gen

from .models import Users
from wli_users.apps.main.serializers import UserSchema
from wli_users.handlers import BaseHandler
from wli_users.utils import Routers, validate_payload


@Routers('/('
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


@Routers('/', name="users-list")
class UsersHandler(BaseHandler):
    schema = UserSchema
    model = Users

    @gen.coroutine
    def get(self):
        cur = self.get_current_user()
        self.write(cur)

    async def post(self, *args, **kwargs):
        payload = self.payload
        password = Users.create_password(payload.pop("password"))
        user = Users(**payload, password=password, guid=uuid.uuid4())
        await asyncio.ensure_future(
            self.upload_files(self.request.files.get("picture"), guid=user.guid))

        id_ = await user.commit()
        self.write(str(id_.inserted_id))
