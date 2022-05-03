import time
from app.user.user_model import UserModel
from app.user.user_schema import UserSchema
from marshmallow import ValidationError
from app import cache


def user_validate(user_data):
    try:
        UserSchema().load(user_data)
        
    except ValidationError:
        raise


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
        raise ValidationError({'user_token': ['Not Found.']})

    if user:
        cache.set('user.%s' % (user.id), user)

        if user.token_expires < time.time():
            raise ValidationError({'user_token': ['Token Expired.']})

        else:
            return user

    else:
        raise ValidationError({'user_token': ['Not Found.']})



