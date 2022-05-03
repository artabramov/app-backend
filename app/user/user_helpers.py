import time
from app.user.user_model import UserModel
from marshmallow import ValidationError
from app import cache


def user_auth(user_token):
    try:
        token_payload = UserModel.get_token_payload(user_token)

    except:
        raise ValidationError({'user_token': ['Incorrect.']})

    user = cache.get('user.%s' % (token_payload['user_id']))
    if not user:
        user = UserModel.query.filter_by(token_signature=token_payload['token_signature'], deleted=0).first()

    elif user.token_signature != token_payload['token_signature']:
        cache.set('user.%s' % (user.id), user)
        raise ValidationError({'token_signature': ['Not Found.']})

    if user:
        cache.set('user.%s' % (user.id), user)

        if user.token_expires < time.time():
            raise ValidationError({'token_signature': ['Token Expired.']})

        else:
            return user

    else:
        raise ValidationError({'token_signature': ['Not Found.']})
