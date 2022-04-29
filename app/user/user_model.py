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
TOKEN_EXPIRATION_TTL = 60 * 60 * 24 * 30

class UserModel(BaseModel):
    __tablename__ = 'users'
    #user_type = db.Column(db.Enum(UserType))

    user_email = db.Column(db.String(255), nullable=False, index=True, unique=True)
    user_name = db.Column(db.String(80), nullable=False)

    pass_hash = db.Column(db.String(128), nullable=False, index=True)
    pass_expires = db.Column(db.Integer(), nullable=False, default=0)
    pass_attempts = db.Column(db.SmallInteger(), default=0)

    token_signature = db.Column(db.String(128), nullable=False, index=True, unique=True)
    token_expires = db.Column(db.Integer(), nullable=False, default=0)

    is_admin = db.Column(db.Boolean(), nullable=False, default=False)
    user_meta = db.relationship('UserMetaModel', backref='users', lazy='subquery')

    def __init__(self, user_email, user_name, is_admin=False):
        #self.user_type = user_type
        self.user_email = user_email.lower()
        self.user_name = user_name
        self.is_admin = is_admin
        self.update_signature()
        self.update_pass()

    @property
    def user_pass(self):
        return self._user_pass

    @user_pass.setter
    def user_pass(self, value):
        self._user_pass = value
        self.pass_hash = UserModel.get_hash(self.user_email + self._user_pass)
        self.pass_expires = time.time() + PASS_EXPIRATION_TTL
        self.pass_attempts = 0

    @staticmethod
    def get_hash(value):
        encoded_value = (value + PASS_HASH_SALT).encode()
        hash_obj = hashlib.sha512(encoded_value)
        return hash_obj.hexdigest()

    def update_pass(self):
        self.user_pass = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=PASS_LENGTH))

    def update_signature(self):
        is_unique = False
        while not is_unique:
            token_signature = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=128))
            if not UserModel.query.filter_by(token_signature=token_signature).count():
                is_unique = True
        self.token_signature = token_signature
        self.token_expires = time.time() + TOKEN_EXPIRATION_TTL

    @property
    def user_token(self):
        token_payload = {
            'user_id': self.id,
            'user_name': self.user_name,
            'token_signature': self.token_signature,
            'token_expires': self.token_expires
        }
        base64_bytes = base64.b64encode(json.dumps(token_payload).encode())
        user_token = base64_bytes.decode('ascii')
        return user_token

    @staticmethod
    def get_payload(user_token):
        try:
            user_token_bytes = base64.b64decode(user_token)
            user_token_string = user_token_bytes.decode('ascii')
            token_payload = json.loads(user_token_string)
            return token_payload

        except Exception as e:
            raise ValidationError({'user_token': ['Incorrect.']})


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
