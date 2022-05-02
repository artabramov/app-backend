from enum import Enum
from app import db
from app.core.base_model import BaseModel
from app.user.user_schema import UserSchema, UserRole
from marshmallow import ValidationError
import random, string
import json
import hmac, base64, struct, hashlib, time
import pyotp

PASS_HASH_SALT = 'abcd'
PASS_ATTEMPTS_LIMIT = 5
PASS_SUSPENSION_TIME = 30

CODE_SECRET_LENGTH = 16
CODE_ATTEMPTS_LIMIT = 5

TOKEN_EXPIRATION_TIME = 60 * 60 * 24 * 30


class UserModel(BaseModel):
    __tablename__ = 'users'
    user_login = db.Column(db.String(40), nullable=False, unique=True)
    user_name = db.Column(db.String(80), nullable=False)
    user_role = db.Column(db.Enum(UserRole), nullable=False, default='nobody')

    pass_hash = db.Column(db.String(128), nullable=False, index=True)
    pass_attempts = db.Column(db.SmallInteger(), nullable=False, default=0)
    pass_suspended = db.Column(db.Integer(), nullable=False, default=0)

    code_secret = db.Column(db.String(32), nullable=False, index=True)
    code_attempts = db.Column(db.SmallInteger(), nullable=False, default=0)

    token_signature = db.Column(db.String(128), nullable=False, index=True, unique=True)
    token_expires = db.Column(db.Integer(), nullable=False, default=0)

    #is_admin = db.Column(db.Boolean(), nullable=False, default=False)
    user_meta = db.relationship('UserMetaModel', backref='users', lazy='subquery')

    def __init__(self, user_login, user_name, user_pass, user_role=None):
        #self.user_type = user_type
        #self.user_email = user_email.lower()
        self.user_login = user_login.lower()
        self.user_name = user_name
        self.user_role = UserRole.editor
        self.user_pass = user_pass
        self.pass_attempts = 0
        self.pass_suspended = 0
        self.set_code_secret()
        self.code_attempts = 0
        self.set_token_signature()
        self.token_expires = time.time() + TOKEN_EXPIRATION_TIME
        #self.is_admin = is_admin

    @property
    def user_pass(self):
        return self._user_pass if hasattr(self, '_user_pass') else None

    @user_pass.setter
    def user_pass(self, value):
        self._user_pass = value
        self.pass_hash = UserModel.get_pass_hash(self.user_login + value)
        #self.pass_suspended = time.time() + PASS_EXPIRATION_TTL

    @staticmethod
    def get_pass_hash(value):
        encoded_value = (value + PASS_HASH_SALT).encode()
        hash_obj = hashlib.sha512(encoded_value)
        return hash_obj.hexdigest()

    def set_code_secret(self):
        #self.code_secret = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=CODE_SECRET_LENGTH))
        self.code_secret = pyotp.random_base32()

    def get_hotp_token(self, intervals_no):
        key = base64.b32decode(self.code_secret, True)
        msg = struct.pack(">Q", intervals_no)
        h = hmac.new(key, msg, hashlib.sha1).digest()
        o = ord(h[19]) & 15
        h = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000
        return h

    def get_totp_token(self):
        return self.get_hotp_token(intervals_no=int(time.time())//30)

    def totp(self):
        """ Calculate TOTP using time and key """
        now = int(time.time() // 30)
        msg = now.to_bytes(8, "big")
        digest = hmac.new(self.code_secret.encode(), msg, "sha1").digest()
        offset = digest[19] & 0xF
        code = digest[offset : offset + 4]
        code = int.from_bytes(code, "big") & 0x7FFFFFFF
        code = code % 1000000
        return "{:06d}".format(code)



    def set_token_signature(self):
        is_unique = False
        while not is_unique:
            token_signature = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=128))
            if not UserModel.query.filter_by(token_signature=token_signature).count():
                is_unique = True
        self.token_signature = token_signature
        

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
            'user_login': user.user_login,
            'user_name': user.user_name,
            'user_role': user.user_role,
            'user_pass': user.user_pass,
            #'pass_attempts': 0,
            #'is_admin': user.is_admin,
        })
        
    except ValidationError:
        raise

    if UserModel.query.filter_by(user_login=user.user_login).first():
        raise ValidationError({'user_login': ['Already exists.']})


@db.event.listens_for(UserModel, 'before_update')
def before_update_user(mapper, connect, user):
    try:
        user_data = {
            'user_name': user.user_name,
            'user_role': user.user_role,
        }

        if user.user_pass:
            user_data['user_pass'] = user.user_pass

        UserSchema().load(user_data)
        
    except ValidationError:
        raise
