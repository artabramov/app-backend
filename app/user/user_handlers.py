import time
from app.user.user_model import User
from app.user_meta.user_meta_model import UserMeta
from marshmallow import ValidationError
from app import app, db, cache, log
import os
import qrcode
from sqlalchemy.exc import SQLAlchemyError
from app.user.user_model import PASS_ATTEMPTS_LIMIT, PASS_SUSPENSION_TIME, CODE_ATTEMPTS_LIMIT
from app.core.json_response import json_response


def user_auth(user_token):
    try:
        token_payload = User.get_token_payload(user_token)
    except:
        raise ValidationError({'user_token': ['Incorrect.']})

    user = cache.get('user.%s' % (token_payload['user_id']))
    if not user:
        user = User.query.filter_by(token_signature=token_payload['token_signature'], deleted=0).first()

    if not user:
        raise ValidationError({'user_token': ['Not Found.']})
        
    elif user.token_signature != token_payload['token_signature']:
        raise ValidationError({'user_token': ['Not Found.']})

    else:
        cache.set('user.%s' % (user.id), user)
        if user.token_expires < time.time():
            raise ValidationError({'user_token': ['Token Expired.']})
        else:
            return user


@json_response
def user_register(user_login, user_name, user_pass, meta_data=None):
    user = User(user_login, user_name, user_pass)
    db.session.add(user)
    db.session.flush()
    user.user_role = 'admin' if user.id == 1 else 'guest'

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


@json_response
def user_signin(user_login, user_code):
    user = User.query.filter_by(user_login=user_login, deleted=0).first()
    
    if not user:
        return {}, {'user_login': ['Not Found'], }, 404
    
    elif user.code_attempts < 1:
        return {}, {'user_code': ['Not Acceptable'], }, 406

    elif user_code == user.code_value:
        if os.path.isfile(app.config['QR_PATH_MASK'] % user.code_key):
            os.remove(app.config['QR_PATH_MASK'] % user.code_key)

        user.code_attempts = 0
        db.session.flush()
        db.session.commit()
        cache.set('user.%s' % (user.id), user)
        return {'user_token': user.user_token}, {}, 200

    else:
        user.code_attempts -= 1
        db.session.flush()
        db.session.commit()
        cache.set('user.%s' % (user.id), user)
        return {}, {'user_code': ['Incorrect'], }, 404


@json_response
def user_signout(user_token):
    authed_user = user_auth(user_token)
    authed_user.token_signature = authed_user.generate_token_signature()
    db.session.flush()
    db.session.commit()
    cache.set('user.%s' % (authed_user.id), authed_user)
    return {}, {}, 200


@json_response
def user_restore(user_login, user_pass):
    user_login = user_login.lower()
    pass_hash = User.get_pass_hash(user_login + user_pass)
    user = User.query.filter_by(user_login=user_login, deleted=0).first()
    if not user:
        return {}, {'user_login': ['Not Found'], }, 404

    elif user.pass_suspended > time.time():
        return {}, {'user_pass': ['Not Acceptable'], }, 406

    elif user.pass_hash == pass_hash:
        user.pass_attempts = PASS_ATTEMPTS_LIMIT
        user.pass_suspended = 0
        user.code_attempts = CODE_ATTEMPTS_LIMIT
        db.session.flush()
        db.session.commit()
        cache.set('user.%s' % (user.id), user)
        return {}, {}, 200

    else:
        user.pass_attempts -= 1
        if user.pass_attempts < 1:
            user.pass_attempts = PASS_ATTEMPTS_LIMIT
            user.pass_suspended = time.time() + PASS_SUSPENSION_TIME

        db.session.flush()
        db.session.commit()
        cache.set('user.%s' % (user.id), user)
        return {}, {'user_pass': ['Not Found'], }, 404


@json_response
def user_select(user_token, user_id):
    authed_user = user_auth(user_token)
    is_admin = authed_user.is_admin()
    can_edit = authed_user.can_edit()
    can_read = authed_user.can_read()

    user = cache.get('user.%s' % (user_id))
    if not user:
        user = User.query.filter_by(id=user_id).first()

    if user:
        cache.set('user.%s' % (user.id), user)
        return {'user': {
            'id': user.id,
            'user_name': user.user_name,
            'user_meta': {meta.meta_key: meta.meta_value for meta in user.meta}    
        }}, {}, 200
    else:
        return {}, {'user_id': ['Not Found']}, 404

