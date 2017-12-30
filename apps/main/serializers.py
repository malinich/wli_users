from marshmallow import Schema, fields, validate

from apps.main.models import Users


class UserSchema(Schema):
    email = fields.Email(required=True)
    guid = fields.UUID(dump_only=True)
    name = fields.String(validate=validate.Length(max=3), required=True)

    @classmethod
    def to_internal(cls, arguments):
        data = {key: arguments[key][0] for key in cls.Meta.to_internal_fields}
        return data

    class Meta:
        to_internal_fields = ['email', 'name']
