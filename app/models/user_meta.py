from app import db
from marshmallow import Schema, fields, validate, ValidationError
import time


class UserMetaSchema(Schema):
    user_id = fields.Int(validate=validate.Range(min=1))
    meta_key = fields.Str(validate=[validate.Length(min=2, max=40), lambda x: x.replace('_', '').isalnum()])
    meta_value = fields.Str(validate=validate.Length(min=1, max=255))


class UserMeta(db.Model):
    __tablename__ = 'users_meta'
    __table_args__ = (db.UniqueConstraint('user_id', 'meta_key', name='users_meta_ukey'),)
    _parent = 'user_id'
    id = db.Column(db.BigInteger, primary_key=True)
    created = db.Column(db.Integer(), nullable=False, default=lambda: int(time.time()))
    updated = db.Column(db.Integer(), nullable=False, default=0, onupdate=lambda: int(time.time()))
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), index=True)
    meta_key = db.Column(db.String(40), index=True, nullable=False)
    meta_value = db.Column(db.String(255), nullable=True)

    def __init__(self, user_id, meta_key, meta_value):
        self.user_id = user_id
        self.meta_key = meta_key
        self.meta_value = meta_value


@db.event.listens_for(UserMeta, 'before_insert')
def before_insert_user_meta(mapper, connect, user_meta):
    UserMetaSchema().load({
        'user_id': user_meta.user_id,
        'meta_key': user_meta.meta_key,
        'meta_value': user_meta.meta_value,
    })

    if UserMeta.query.filter_by(user_id=user_meta.user_id, meta_key=user_meta.meta_key).first():
        raise ValidationError({'meta_key': ['Already exists.']})


@db.event.listens_for(UserMeta, 'before_update')
def before_update_user_meta(mapper, connect, user_meta):
    UserMetaSchema().load({
        'user_id': user_meta.user_id,
        'meta_key': user_meta.meta_key,
        'meta_value': user_meta.meta_value,
    })

