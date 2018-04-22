import hashlib
import uuid

from marshmallow import validate
from umongo import Document, fields

from wli_users.app import MetaBaseTemplate


class Users(Document, metaclass=MetaBaseTemplate):
    __collection__ = "users"
    email = fields.EmailField(required=True, unique=True)
    guid = fields.UUIDField(missing=uuid.uuid4)
    name = fields.StringField(validate=validate.Length(max=50), required=True)
    picture = fields.UrlField()
    password = fields.StringField(load_only=True)

    class Meta:
        pass
        # indexes = ("email",)

    @classmethod
    def create_password(cls, passwd):
        m = hashlib.sha256()
        m.update(passwd)
        return m.digest()
