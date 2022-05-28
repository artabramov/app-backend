from app import db
from app.core.base_model import BaseModel
from marshmallow import ValidationError
from marshmallow import Schema, fields, validate

USER_PROP_KEYS = {'key_1', 'key_2', 'key_3', 'key_4'}


class UserPropSchema(Schema):
    user_id = fields.Int(validate=validate.Range(min=1))
    prop_key = fields.Str(validate=lambda x: x in USER_PROP_KEYS)
    prop_value = fields.Str(validate=validate.Length(min=1, max=255))


class UserProp(BaseModel):
    __tablename__ = 'users_props'
    __table_args__ = (db.UniqueConstraint('user_id', 'prop_key', name='users_props_ukey'),)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), index=True)
    prop_key = db.Column(db.String(40), index=True, nullable=False)
    prop_value = db.Column(db.String(255), nullable=True)

    def __init__(self, user_id, prop_key, prop_value):
        self.user_id = user_id
        self.prop_key = prop_key
        self.prop_value = prop_value

    @classmethod
    def set_prop(cls, user_id, prop_key, prop_value):
        user_prop = cls.query.filter_by(user_id=user_id, prop_key=prop_key).first()
        if user_prop:
            user_prop.prop_value = prop_value
            user_prop.deleted = 0
        else:
            user_prop = cls(user_id, prop_key, prop_value)
        return user_prop


@db.event.listens_for(UserProp, 'before_insert')
def before_insert_user_prop(mapper, connect, user_prop):
    UserPropSchema().load({
        'user_id': user_prop.user_id,
        'prop_key': user_prop.prop_key,
        'prop_value': user_prop.prop_value,
    })

    if UserProp.query.filter_by(user_id=user_prop.user_id, prop_key=user_prop.prop_key).first():
        raise ValidationError({'prop_key': ['Already exists.']})


@db.event.listens_for(UserProp, 'before_update')
def before_update_user(mapper, connect, user_prop):
    UserPropSchema().load({
        'user_id': user_prop.user_id,
        'prop_key': user_prop.prop_key,
        'prop_value': user_prop.prop_value,
    })
