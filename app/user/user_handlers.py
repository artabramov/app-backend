import time
from app.user.user import User
from app.user.user_meta import UserMeta
from marshmallow import ValidationError
from app import app, db, cache, log
import os
import qrcode
from sqlalchemy.exc import SQLAlchemyError
from app.user.user import PASS_ATTEMPTS_LIMIT, PASS_SUSPEND_TIME, TOTP_ATTEMPTS_LIMIT
from app.core.app_response import app_response


def qrcode_create(totp_key, user_login):
    # TODO: make exception in app_response
    qr = qrcode.make(app.config['QRCODES_REF'] % (totp_key, user_login))
    qr.save(app.config['QRCODES_PATH'] % totp_key)


def qrcode_remove(totp_key):
    if os.path.isfile(app.config['QRCODES_PATH'] % totp_key):
        os.remove(app.config['QRCODES_PATH'] % totp_key)


def user_exists(**kwargs):
    user = user_select(**kwargs)
    return user is not None


def user_insert(user_login, user_name, user_pass, user_role, user_meta=None):
    user = User(user_login, user_name, user_pass, user_role)
    db.session.add(user)
    db.session.flush()

    if user_meta:
        for meta_key in user_meta:
            meta_value = user_meta[meta_key]
            meta = UserMeta(user.id, meta_key, meta_value)
            db.session.add(meta)
        db.session.flush()

    cache.set('user.%s' % (user.id), user)
    return user


def user_select(**kwargs):
    user = None

    if 'id' in kwargs and len(kwargs) == 1:
        user = cache.get('user.%s' % (kwargs['id']))

    if not user:
        user = User.query.filter_by(**kwargs).first()

    if user:
        cache.set('user.%s' % (user.id), user)

    return user


def user_update(user, **kwargs):
    for key in [x for x in kwargs if x != 'user_meta']:
        value = kwargs[key]
        setattr(user, key, value)
    db.session.add(user)
    db.session.flush()

    if 'user_meta' in kwargs:
        for meta_key in kwargs['user_meta']:
            meta_value = kwargs['user_meta'][meta_key]

            user_meta = UserMeta.query.filter_by(user_id=user.id, meta_key=meta_key).first()
            if user_meta and meta_value:
                user_meta.meta_value = meta_value
                user_meta.deleted = 0
                db.session.add(user_meta)

            elif user_meta and not meta_value:
                db.session.delete(user_meta)

            elif not user_meta and meta_value:
                user_meta = UserMeta(user.id, meta_key, meta_value)
                db.session.add(user_meta)

        db.session.flush()

    cache.set('user.%s' % (user.id), user)
    return user


def user_delete(user):
    user.delete()
    db.session.add(user)
    db.session.flush()

    cache.delete('user.%s' % (user.id))
    return True


def user_auth(user_token):
    try:
        token_payload = User.get_token_payload(user_token)
        token_signature = token_payload['token_signature']
        user_id = token_payload['user_id']
    except:
        raise ValidationError({'user_token': ['user_token is incorrect']})

    user = user_select(id=user_id)
    if not user:
        raise ValidationError({'user_token': ['token_token not found']})

    elif user.deleted > 0:
        raise ValidationError({'user_token': ['user_token deleted']})
        
    elif user.token_signature != token_signature:
        raise ValidationError({'user_token': ['user_token is invalid']})

    elif user.token_expires < time.time():
        raise ValidationError({'user_token': ['user_token expired']})

    else:
        return user
