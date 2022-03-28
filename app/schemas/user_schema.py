from marshmallow import Schema, fields, validate
from marshmallow_enum import EnumField
from enum import Enum

class UserStatus(Enum):
    pending = 1
    approved = 2
    trash = 3


class UserSchema(Schema):
    user_email = fields.Email(validate=validate.Length(min=8, max=255))
    user_name = fields.Str(validate=validate.Length(min=4, max=40))
    user_pass = fields.Str(validate=validate.Length(min=8, max=20))
    user_status = EnumField(UserStatus)

