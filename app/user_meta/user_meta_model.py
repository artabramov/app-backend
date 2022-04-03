from app import db
from app.core.base_model import BaseModel
from app.user_meta.user_meta_schema import UserMetaSchema
from marshmallow import ValidationError


class UserMetaModel(BaseModel):
    __tablename__ = 'users_meta'
    __table_args__ = (db.UniqueConstraint('user_id', 'meta_key', name='users_meta_ukey'),)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), index=True)
    meta_key = db.Column(db.String(40), index=True, nullable=False)
    meta_value = db.Column(db.String(255), nullable=True)

    def __init__(self, user_id, meta_key, meta_value):
        self.user_id = user_id
        self.meta_key = meta_key
        self.meta_value = meta_value


@db.event.listens_for(UserMetaModel, 'before_insert')
def before_insert_user(mapper, connect, user_meta):
    try:
        UserMetaSchema().load({
            'user_id': user_meta.user_id,
            'meta_key': user_meta.meta_key,
            'meta_value': user_meta.meta_value,
        })
        
    except ValidationError:
        raise

    if UserMetaModel.query.filter_by(user_id=user_meta.user_id, meta_key=user_meta.meta_key).first():
        raise ValidationError({'meta_key': ['Already exists.']})
