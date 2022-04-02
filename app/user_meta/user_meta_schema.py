from marshmallow import Schema, fields, validate


class UserMetaSchema(Schema):
    user_id = fields.Int(validate=validate.Range(min=1))
    meta_key = fields.Str(validate=validate.Length(min=2, max=40))
    meta_value = fields.Str(validate=validate.Length(min=1, max=255))
