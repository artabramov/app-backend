from enum import Enum
import hashlib
from app import db
from app.core.base_model import BaseModel
from app.user.user_schema import UserSchema
from app.user.user_schema import UserType, UserStatus
from marshmallow import ValidationError
import random, string
from datetime import datetime, timedelta

PASS_HASH_SALT = 'abcd'
SUSPENDED_TIME = 60 * 2
CONFIRM_CODE_LENGTH = 8
CONFIRM_CODE_TIME = 60 * 2
ACCESS_TOKEN_SALT = 'abcd'
ACCESS_TOKEN_TIME = 60 * 2
REFRESH_TOKEN_LENGTH = 128
REFRESH_TOKEN_TIME = 60 * 60 * 24 * 1


class UserModel(BaseModel):
    __tablename__ = 'users'
    lockout_to = db.Column(db.DateTime(timezone=False), default='1970-01-01 00:00:00', nullable=False) # user is blocked until
    user_type = db.Column(db.Enum(UserType))
    user_status = db.Column(db.Enum(UserStatus), nullable=False)
    user_email = db.Column(db.String(255), nullable=False, index=True, unique=True)
    user_name = db.Column(db.String(128), nullable=False)
    pass_hash = db.Column(db.String(128), nullable=False, index=True)
    pass_attempts = db.Column(db.SmallInteger(), default=0)
    #is_admin = db.Column(db.Boolean(), default=False)
    confirm_code = db.Column(db.String(8), nullable=True)
    confirm_to = db.Column(db.DateTime(timezone=False), default='1970-01-01 00:00:00', nullable=False) # confirm code is active until
    refresh_token = db.Column(db.String(128), nullable=False, index=True, unique=True)
    refresh_to = db.Column(db.DateTime(timezone=False), default='1970-01-01 00:00:00', nullable=False) # refresh token is active until
    user_meta = db.relationship('UserMetaModel', backref='users')

    def __init__(self, user_email, user_pass, user_name, user_type='user', user_status='pending'):
        self.user_type = user_type
        self.user_status = user_status
        self.user_email = user_email.lower()
        self.user_pass = user_pass
        self.user_name = user_name

    @property
    def user_pass(self):
        return self.__user_pass

    @user_pass.setter
    def user_pass(self, value):
        self.__user_pass = value
        self.pass_hash = self._get_hash(self.user_email + self.__user_pass + PASS_HASH_SALT)

    def _get_hash(self, value):
        encoded_value = (value).encode()
        hash_obj = hashlib.sha512(encoded_value)
        return hash_obj.hexdigest()

    def _create_refresh_token(self):
        unique_token_found = False
        while not unique_token_found:
            refresh_token = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=REFRESH_TOKEN_LENGTH))
            if UserModel.query.filter_by(refresh_token=refresh_token).count() is 0:
                unique_token_found = True
        return refresh_token

    def _create_confirm_code(self):
        return ''.join(random.choices(string.digits, k=CONFIRM_CODE_LENGTH))


@db.event.listens_for(UserModel, 'before_insert')
def before_insert_user(mapper, connect, user):
    try:
        UserSchema().load({
            'user_type': user.user_type,
            'user_status': user.user_status,
            'user_email': user.user_email,
            'user_pass': user.user_pass,
            'user_name': user.user_name,
            #'pass_attempts': 0,
            #'is_admin': user.is_admin,
        })
        
        user.confirm_code = user._create_confirm_code()
        user.confirm_to = datetime.now() + timedelta(seconds=CONFIRM_CODE_TIME)
        user.refresh_token = user._create_refresh_token()
        user.refresh_to = datetime.now() + timedelta(seconds=REFRESH_TOKEN_TIME)
        
    except ValidationError:
        raise

    if UserModel.query.filter_by(user_email=user.user_email).first():
        raise ValidationError({'user_email': ['Already exists.']})
