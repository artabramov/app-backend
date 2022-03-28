from marshmallow import Schema, fields, validate
#from models.user_model import UserModel


class UserSchema(Schema):
    user_email = fields.Email(validate=validate.Length(min=8, max=255))
    user_name = fields.Str(validate=validate.Length(min=4, max=40))
    user_pass = fields.Str(validate=validate.Length(min=8, max=20))

    #def __init__(self):
    #    self.user_model = None
