from marshmallow import Schema, fields, validate

USER_META_KEYS = {'user_timezone', 'user_language', 'user_image'}


class UserMetaSchema(Schema):
    user_id = fields.Int(validate=validate.Range(min=1))
    meta_key = fields.Str(validate=lambda x: x in USER_META_KEYS)
    meta_value = fields.Str(validate=validate.Length(min=1, max=255))
