import time
from app.user.user_model import UserModel
from marshmallow import ValidationError


def user_auth(user_token):
    try:
        token_payload = UserModel.get_payload(user_token)

    except:
        raise ValidationError({'user_token': ['Incorrect.']})

    user = UserModel.query.filter_by(token_signature=token_payload['token_signature'], deleted=0).first()
    if not user:
        raise ValidationError({'token_signature': ['Not Found.']})

    elif user.token_expires < time.time():
        raise ValidationError({'token_signature': ['Token Expired.']})

    return user
