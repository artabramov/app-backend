from marshmallow import Schema, fields, validate
#from marshmallow_enum import EnumField
#from enum import Enum


#class UserType(Enum):
#    user = 0
#    admin = 1
#    root = 2


class UserSchema(Schema):
    #user_type = EnumField(UserType)
    user_email = fields.Email(validate=validate.Length(min=8, max=255))
    #user_pass = fields.Str(validate=validate.Length(min=8, max=20))
    #pass_hash = fields.Str(validate=validate.Length(equal=64))
    user_name = fields.Str(validate=validate.Length(min=4, max=40))
    #pass_attempts = fields.Int(validate=validate.Range(min=0, max=5))
    #is_admin = fields.Boolean()

