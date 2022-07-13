from flask import g
from app import app, db
from app.mixins.meta_mixin import MetaMixin
from app.mixins.enum_mixin import EnumMixin
from marshmallow import Schema, fields, validate, ValidationError
from marshmallow_enum import EnumField
import random, string, json
import base64, hashlib, time, pyotp
from app import err
from sqlalchemy.orm import backref


USER_PASS_HASH_SALT = app.config['USER_PASS_HASH_SALT']
USER_TOKEN_EXPIRATION_TIME = app.config['USER_TOKEN_EXPIRATION_TIME']


class UserStatus(EnumMixin):
    blank = 0
    reader = 1
    editor = 2
    admin = 3


class UserSchema(Schema):
    user_login = fields.Str(validate=[validate.Length(min=4, max=40), lambda x: x.isalnum()])
    user_summary = fields.Str(validate=validate.Length(max=255))
    user_status = EnumField(UserStatus, by_value=True)
    user_pass = fields.Str(validate=validate.Length(min=4))


class User(db.Model, MetaMixin):
    __tablename__ = 'users'
    id = db.Column(db.BigInteger, primary_key=True)
    created = db.Column(db.Integer(), nullable=False, default=lambda: int(time.time()))
    updated = db.Column(db.Integer(), nullable=False, default=0, onupdate=lambda: int(time.time()))
    user_login = db.Column(db.String(40), nullable=False, unique=True)
    user_summary = db.Column(db.String(255), nullable=True)
    user_status = db.Column(db.Enum(UserStatus), nullable=False)
    pass_hash = db.Column(db.String(128), nullable=False, index=True)
    pass_attempts = db.Column(db.SmallInteger(), nullable=False, default=0)
    pass_suspended = db.Column(db.Integer(), nullable=False, default=0)
    totp_key = db.Column(db.String(32), nullable=False, index=True)
    totp_attempts = db.Column(db.SmallInteger(), nullable=False, default=0)
    token_signature = db.Column(db.String(128), nullable=False, index=True, unique=True)
    token_expires = db.Column(db.Integer(), nullable=False, default=0)

    meta = db.relationship('UserMeta', backref='user', lazy='subquery')
    volumes = db.relationship('Volume', lazy='subquery', cascade='all, delete-orphan', backref=backref('user', cascade='delete'), single_parent=True)
    categories = db.relationship('Category', backref='user', lazy='subquery')
    posts = db.relationship('Post', backref='user', lazy='subquery')
    comments = db.relationship('Comment', backref='user', lazy='subquery')
    uploads = db.relationship('Upload', backref='user', lazy='subquery')

    def __init__(self, user_login, user_pass):
        self.user_login = user_login
        self.user_summary = None
        self.user_status = 'blank'
        self.user_pass = user_pass
        self.pass_attempts = 0
        self.pass_suspended = 0
        self.totp_key = self.generate_totp_key()
        self.totp_attempts = 0
        self.token_signature = self.generate_token_signature()
        self.token_expires = time.time() + USER_TOKEN_EXPIRATION_TIME

    def __setattr__(self, name, value):
        if name == 'user_status':
            super().__setattr__('user_status', UserStatus.get_enum(user_status=value))
        else:
            super().__setattr__(name, value)


    @property
    def user_pass(self):
        return self._user_pass if hasattr(self, '_user_pass') else None # TODO: WTF???

    @user_pass.setter
    def user_pass(self, value):
        self._user_pass = value
        self.pass_hash = User.get_pass_hash(self.user_login + value)

    @staticmethod
    def get_pass_hash(value):
        encoded_value = (value + USER_PASS_HASH_SALT).encode()
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
            raise ValidationError({'user_token': [err.INVALID_VALUE]})

    @property
    def can_admin(self):
        return self.user_status == UserStatus.admin

    @property
    def can_edit(self):
        return self.user_status in [UserStatus.admin, UserStatus.editor]

    @property
    def can_read(self):
        return self.user_status in [UserStatus.admin, UserStatus.editor, UserStatus.reader]


@db.event.listens_for(User, 'before_insert')
def before_insert_user(mapper, connect, user):
    user_data = {
        'user_login': user.user_login,
        'user_pass': user.user_pass,
        'user_status': user.user_status,
    }

    if user.user_summary:
        user_data['user_summary'] = user.user_summary
        
    UserSchema().load(user_data)

    if User.query.filter_by(user_login=user.user_login).first():
        raise ValidationError({'user_login': [err.ALREADY_EXISTS]})


@db.event.listens_for(User, 'before_update')
def before_update_user(mapper, connect, user):
    user_data = {}

    if user.user_status:
        user_data['user_status'] = user.user_status

    if user.user_summary:
        user_data['user_summary'] = user.user_summary

    if user.user_pass:
        user_data['user_pass'] = user.user_pass

    UserSchema().load(user_data)

