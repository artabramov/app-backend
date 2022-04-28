from enum import Enum
import hashlib
from app import db
from app.core.base_model import BaseModel
from app.user.user_schema import UserSchema
#from app.user.user_schema import UserType
from marshmallow import ValidationError
import random, string
import time
import base64
import json

PASS_LENGTH = 8
PASS_HASH_SALT = 'abcd'
PASS_ATTEMPTS_LIMIT = 5
PASS_EXPIRATION_TTL = 60 * 1

class UserModel(BaseModel):
    __tablename__ = 'users'

    #user_type = db.Column(db.Enum(UserType))
    user_email = db.Column(db.String(255), nullable=False, index=True, unique=True)
    user_name = db.Column(db.String(80), nullable=False)
    user_token = db.Column(db.String(128), nullable=False, index=True, unique=True)

    pass_hash = db.Column(db.String(128), nullable=False, index=True)
    pass_expires = db.Column(db.Integer(), nullable=False, default=0)
    pass_attempts = db.Column(db.SmallInteger(), default=0)

    is_admin = db.Column(db.Boolean(), nullable=False, default=False)
    user_meta = db.relationship('UserMetaModel', backref='users', lazy='subquery')

    def __init__(self, user_email, user_name, is_admin=False):
        #self.user_type = user_type
        self.user_email = user_email.lower()
        self.user_name = user_name
        self.is_admin = is_admin
        self.update_token()
        self.update_pass()
        

    @property
    def user_pass(self):
        return self.__user_pass

    @user_pass.setter
    def user_pass(self, value):
        self.__user_pass = value
        self.pass_hash = UserModel.get_hash(self.user_email + self.__user_pass)
        self.pass_expires = time.time() + PASS_EXPIRATION_TTL
        self.pass_attempts = 0

    @staticmethod
    def get_hash(value):
        encoded_value = (value + PASS_HASH_SALT).encode()
        hash_obj = hashlib.sha512(encoded_value)
        return hash_obj.hexdigest()

    def update_pass(self):
        self.user_pass = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=PASS_LENGTH))

    def update_token(self):
        is_unique = False
        while not is_unique:
            user_token = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=128))
            if not UserModel.query.filter_by(user_token=user_token).count():
                is_unique = True
        self.user_token = user_token

    #def create_code(self):
        #return ''.join(random.choices(string.digits, k=RESET_CODE_LENGTH))
        #self.reset_expires = time.time() + RESET_CODE_TIME

    @property
    def user_cookie(self):
        user_data = {
            'user_id': self.id,
            'user_name': self.user_name,
            'user_token': self.user_token
        }
        base64_bytes = base64.b64encode(json.dumps(user_data).encode())
        return base64_bytes.decode('ascii')

    @staticmethod
    def decode_cookie(user_cookie):
        user_cookie_bytes = base64.b64decode(user_cookie)
        user_cookie_string = user_cookie_bytes.decode('ascii')
        user_cookie = json.loads(user_cookie_string)
        return user_cookie


@db.event.listens_for(UserModel, 'before_insert')
def before_insert_user(mapper, connect, user):
    try:
        UserSchema().load({
            #'user_type': user.user_type,
            'user_email': user.user_email,
            #'user_pass': user.user_pass,
            'user_name': user.user_name,
            #'pass_attempts': 0,
            #'is_admin': user.is_admin,
        })
        
    except ValidationError:
        raise

    if UserModel.query.filter_by(user_email=user.user_email).first():
        raise ValidationError({'user_email': ['Already exists.']})


@db.event.listens_for(UserModel, 'before_update')
def before_insert_user(mapper, connect, user):
    try:
        UserSchema().load({
            'user_name': user.user_name,
        })
        
    except ValidationError:
        raise
