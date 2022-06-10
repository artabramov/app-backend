import flask
from flask import request
from marshmallow import ValidationError
from app.core.primary_handlers import select
from app.user.user import User
import time


def user_auth(func):
    def inner(*args, **kwargs):
        user_token = request.headers.get('user_token')

        try:
            token_payload = User.get_token_payload(user_token)
            token_signature = token_payload['token_signature']
            user_id = token_payload['user_id']
        except:
            raise ValidationError({'user_token': ['user_token is incorrect']})

        user = select(User, id=user_id)
        if not user:
            raise ValidationError({'user_token': ['token_token not found']})

        elif user.deleted > 0:
            raise ValidationError({'user_token': ['user_token deleted']})
            
        elif user.token_signature != token_signature:
            raise ValidationError({'user_token': ['user_token is invalid']})

        elif user.token_expires < time.time():
            raise ValidationError({'user_token': ['user_token expired']})

        else:
            flask.g.user = user

        return func(*args, **kwargs)
    return inner
