from app import app
from app import db
import enum
import werkzeug
import re
import hashlib
from app.models.base_model import BaseModel


class UserStatus(enum.Enum):
    pending = 1
    approved = 2
    trash = 3


class User(BaseModel):
    __tablename__ = 'users'
    __user_password = ''
    restored_date = db.Column(db.DateTime(timezone=False), server_default='1970-01-01 00:00:00', nullable=False)
    authed_date = db.Column(db.DateTime(timezone=False), server_default='1970-01-01 00:00:00', nullable=False)
    user_status = db.Column(db.Enum(UserStatus), nullable=False)
    user_email = db.Column(db.String(255), nullable=False, index=True, unique=True)
    user_name = db.Column(db.String(40), nullable=False)
    password_hash = db.Column(db.String(64), nullable=False)
    password_attempts = db.Column(db.SmallInteger, nullable=False)

    def __init__(self, user_email, user_password, user_name, user_status='pending'):
        self.user_status = user_status
        self.user_email = user_email
        self.user_name = user_name
        self.user_password = user_password
        self.password_attempts = 0

    @property
    def user_password(self):
        return self.__user_password
