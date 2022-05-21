import time
from app.user.user_model import User
from app.user_meta.user_meta_model import UserMeta
from marshmallow import ValidationError
from app import app, db, cache, log


def user_auth(user_token):
    try:
        token_payload = User.get_token_payload(user_token)
    except:
        raise ValidationError({'user_token': ['Incorrect.']})

    user = cache.get('user.%s' % (token_payload['user_id']))
    if not user:
        user = User.query.filter_by(token_signature=token_payload['token_signature'], deleted=0).first()
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


import qrcode
from sqlalchemy.exc import SQLAlchemyError
def user_register(user_login, user_name, user_pass, meta_data=None):
    try:
        user = User(user_login, user_name, user_pass)
        db.session.add(user)
        db.session.flush()
        user.user_role = 'admin' if user.id == 1 else 'nobody'

        if meta_data:
            for meta_key in meta_data:
                meta_value = meta_data[meta_key]
                user_meta = UserMeta(user.id, meta_key, meta_value)
                db.session.add(user_meta)
            db.session.flush()

        qr = qrcode.make(app.config['QR_LINK_MASK'] % (user.code_key, user.user_login))
        qr.save(app.config['QR_PATH_MASK'] % user.code_key)

        db.session.commit()
        cache.set('user.%s' % (user.id), user)
        return {
            'code_key': user.code_key, 
            'code_qr': app.config['QR_URI_MASK'] % user.code_key
        }, {}, 201

    except ValidationError as e:
        log.debug(e.messages)
        db.session.rollback()
        return {}, e.messages, 400

    except SQLAlchemyError as e:
        log.error(e)
        db.session.rollback()
        return {}, {'error': ['Service Unavailable']}, 503

    except Exception as e:
        log.error(e)
        db.session.rollback()
        return {}, {'error': ['Internal Server Error']}, 500
