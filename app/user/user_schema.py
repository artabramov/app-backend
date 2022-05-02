from marshmallow import Schema, fields, validate
from marshmallow.validate import And
from marshmallow_enum import EnumField
from enum import Enum


class UserRole(Enum):
    newbie = 0
    reader = 1
    editor = 2
    admin = 3


class UserSchema(Schema):
    #user_email = fields.Email(validate=validate.Length(min=8, max=255))
    #pass_hash = fields.Str(validate=validate.Length(equal=64))
    user_login = fields.Str(validate=[validate.Length(min=4, max=40), lambda x: x.isalnum()])
    user_name = fields.Str(validate=validate.Length(min=4, max=80))
    user_role = EnumField(UserRole, by_value=True)
    user_pass = fields.Str(validate=validate.Length(min=4))
    #pass_attempts = fields.Int(validate=validate.Range(min=0, max=5))
    #is_admin = fields.Boolean()
