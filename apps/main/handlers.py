from uuid import UUID

from tornado import gen

from apps.main.models import Users
from apps.main.serializers import UserSchema
from handlers import BaseHandler
from utils import Router, validate_payload


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

    @gen.coroutine
    def get(self):
        self.render("templates/main.html")

    @validate_payload(UserSchema)
    async def post(self, *args, **kwargs):
        user = Users(**self.payload)
        id_ = await user.commit()
        self.write(str(id_.inserted_id))
