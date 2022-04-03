from enum import Enum
import hashlib
from app import db
from app.core.base_model import BaseModel
from app.user.user_schema import UserSchema
from app.user.user_schema import UserStatus
from marshmallow import ValidationError

PASS_SALT = '123'


class UserModel(BaseModel):
    __tablename__ = 'users'
    expired_date = db.Column(db.DateTime(timezone=False), server_default='1970-01-01 00:00:00', nullable=False)
    user_email = db.Column(db.String(255), nullable=False, index=True, unique=True)
    user_name = db.Column(db.String(128), nullable=False)
    pass_hash = db.Column(db.String(128), nullable=False)
    user_status = db.Column(db.Enum(UserStatus), nullable=False)
    user_meta = db.relationship('UserMetaModel', backref='users')

    def __init__(self, user_email, user_pass, user_name, user_status='pending'):
        self.user_email = user_email
        self.user_pass = user_pass
        self.user_name = user_name
        self.user_status = user_status

    @property
    def user_pass(self):
        return self.__user_pass

    @user_pass.setter
    def user_pass(self, value):
        self.__user_pass = value
        self.pass_hash = self._get_pass_hash(value)

    def _get_pass_hash(self, user_pass):
        encoded_pass = (user_pass + PASS_SALT).encode()
        hash_obj = hashlib.sha256(encoded_pass)
        return hash_obj.hexdigest()


@db.event.listens_for(UserModel, 'before_insert')
def before_insert_user(mapper, connect, user):
    try:
        UserSchema().load({
            'user_email': user.user_email,
            'user_name': user.user_name,
            'user_pass': user.user_pass,
            'user_status': user.user_status,
        })
        
    except ValidationError:
        raise

    if UserModel.query.filter_by(user_email=user.user_email).first():
        raise ValidationError({'user_email': ['Already exists.']})
