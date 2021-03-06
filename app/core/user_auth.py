import flask
from flask import request
from marshmallow import ValidationError
from app.core.basic_handlers import select
from app.models.user import User
from app import err
import time


def user_auth(func):
    def inner(*args, **kwargs):
        user_token = request.headers.get('user_token')

        if not user_token:
            raise ValidationError({'user_token': [err.EMPTY_VALUE]})

        try:
            token_payload = User.get_token_payload(user_token)
            token_signature = token_payload['token_signature']
            user_id = token_payload['user_id']
        except:
            raise ValidationError({'user_token': [err.INVALID_VALUE]})

        user = select(User, id=user_id)
        if not user:
            raise ValidationError({'user_token': [err.VALUE_NOT_FOUND]})

        elif user.user_status.name == 'blank':
            raise ValidationError({'user_token': [err.PERMISSION_DENIED]})
            
        elif user.token_signature != token_signature:
            raise ValidationError({'user_token': [err.INVALID_VALUE]})

        elif user.token_expires < time.time():
            raise ValidationError({'user_token': [err.PERMISSION_EXPIRED]})

        else:
            flask.g.user = user

        return func(*args, **kwargs)
    return inner
