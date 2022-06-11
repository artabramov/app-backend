from enum import Enum
from app import db
from app.core.primary_model import BasicModel
from app.core.meta_mixin import MetaMixin
import random, string
import json
import base64, hashlib, time, pyotp
from marshmallow import Schema, fields, validate, ValidationError
from marshmallow_enum import EnumField
#from app.user.user_meta import UserMeta

PASS_HASH_SALT = 'abcd'
PASS_ATTEMPTS_LIMIT = 5
PASS_SUSPEND_TIME = 30

TOTP_KEY_LENGTH = 16
TOTP_ATTEMPTS_LIMIT = 5

TOKEN_EXPIRATION_TIME = 60 * 60 * 24 * 7


class UserRole(Enum):
    guest = 0
    reader = 1
    editor = 2
    admin = 3

    @classmethod
    def get_role(cls, user_role):
        return cls._member_map_[user_role] if user_role in cls._member_map_ else user_role


class UserSchema(Schema):
    user_login = fields.Str(validate=[validate.Length(min=4, max=40), lambda x: x.isalnum()])
    user_name = fields.Str(validate=validate.Length(min=4, max=80))
    user_role = EnumField(UserRole, by_value=True)
    user_pass = fields.Str(validate=validate.Length(min=4))
    user_code = fields.Int(validate=validate.Range(min=0, max=999999))


class User(BasicModel, MetaMixin):
    __tablename__ = 'users'
    user_login = db.Column(db.String(40), nullable=False, unique=True)
    user_name = db.Column(db.String(80), nullable=False)
    user_role = db.Column(db.Enum(UserRole), nullable=False, default='guest')

    pass_hash = db.Column(db.String(128), nullable=False, index=True)
    pass_attempts = db.Column(db.SmallInteger(), nullable=False, default=0)
    pass_suspended = db.Column(db.Integer(), nullable=False, default=0)

    totp_key = db.Column(db.String(32), nullable=False, index=True)
    totp_attempts = db.Column(db.SmallInteger(), nullable=False, default=0)

    token_signature = db.Column(db.String(128), nullable=False, index=True, unique=True)
    token_expires = db.Column(db.Integer(), nullable=False, default=0)

    meta = db.relationship('UserMeta', backref='users', lazy='subquery')

    def __init__(self, user_login, user_name, user_pass, user_role):
        self.user_login = user_login.lower()
        self.user_name = user_name
        self.user_role = user_role
        self.user_pass = user_pass
        self.pass_attempts = 0
        self.pass_suspended = 0
        self.totp_key = self.generate_totp_key()
        self.totp_attempts = 0
        self.token_signature = self.generate_token_signature()
        self.token_expires = time.time() + TOKEN_EXPIRATION_TIME

    @property
    def user_pass(self):
        return self._user_pass if hasattr(self, '_user_pass') else None

    @user_pass.setter
    def user_pass(self, value):
        self._user_pass = value
        self.pass_hash = User.get_pass_hash(self.user_login + value)

    @staticmethod
    def get_pass_hash(value):
        encoded_value = (value + PASS_HASH_SALT).encode()
        hash_obj = hashlib.sha512(encoded_value)
        return hash_obj.hexdigest()

    def generate_totp_key(self):
        return pyotp.random_base32()

    @property
    def user_totp(self):
        totp = pyotp.TOTP(self.totp_key)
        return totp.now()

    def generate_token_signature(self):
        is_unique = False
        while not is_unique:
            token_signature = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=128))
            if not User.query.filter_by(token_signature=token_signature).count():
                is_unique = True
        return token_signature

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
    def get_token_payload(user_token):
        try:
            user_token_bytes = base64.b64decode(user_token)
            user_token_string = user_token_bytes.decode('ascii')
            token_payload = json.loads(user_token_string)
            return token_payload

        except Exception as e:
            raise ValidationError({'user_token': ['Incorrect.']})

    @property
    def can_admin(self):
        return self.user_role == UserRole.admin

    @property
    def can_edit(self):
        return self.user_role in [UserRole.admin, UserRole.editor]

    @property
    def can_read(self):
        return self.user_role in [UserRole.admin, UserRole.editor, UserRole.reader]



@db.event.listens_for(User, 'before_insert')
def before_insert_user(mapper, connect, user):
    UserSchema().load({
        'user_login': user.user_login,
        'user_name': user.user_name,
        'user_pass': user.user_pass,
        'user_role': UserRole.get_role(user.user_role),
    })

    if User.query.filter_by(user_login=user.user_login).first():
        raise ValidationError({'user_login': ['Already exists.']})


@db.event.listens_for(User, 'before_update')
def before_update_user(mapper, connect, user):
    user_data = {
        'user_name': user.user_name,
        'user_role': UserRole.get_role(user.user_role),
    }

    if user.user_pass:
        user_data['user_pass'] = user.user_pass

    UserSchema().load(user_data)
