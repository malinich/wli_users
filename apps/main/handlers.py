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
        tram = yield Users.find_one(guid=guid)
        self.write("tram %s" % tram)


@Router('/', name="users-list")
class UsersHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        self.render("templates/main.html")

    @validate_payload(UserSchema)
    async def post(self, *args, **kwargs):
        data = UserSchema.to_internal(self.request.arguments)
        user = Users(**data)
        id_ = await user.commit()
        self.write("user: %s" % id_.inserted_id)
