import time
from app.user.user import User
from app.user.user_meta import UserMeta
from marshmallow import ValidationError
from app import app, db, cache, log
import os
import qrcode
from sqlalchemy.exc import SQLAlchemyError
from app.user.user import PASS_ATTEMPTS_LIMIT, PASS_SUSPENSION_TIME, TOTP_ATTEMPTS_LIMIT
from app.core.app_response import app_response


def qrcode_create(totp_key, user_login):
    # TODO: make exception in app_response
    qr = qrcode.make(app.config['QRCODES_REF'] % (totp_key, user_login))
    qr.save(app.config['QRCODES_PATH'] % totp_key)
    return True


def qrcode_remove(totp_key):
    if os.path.isfile(app.config['QRCODES_PATH'] % totp_key):
        os.remove(app.config['QRCODES_PATH'] % totp_key)
    return True


def user_exists(**kwargs):
    user = user_select(**kwargs)
    return user is not None


def user_insert(user_login, user_name, user_pass, user_role, user_meta):
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
    for key in kwargs:
        value = kwargs[key]
        setattr(user, key, value)

    db.session.add(user)
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










def _user_signin(user_login, user_code):
    user = User.query.filter_by(user_login=user_login, deleted=0).first()
    
    if not user:
        return {}, {'user_login': ['Not Found'], }, 404
    
    elif user.totp_remains < 1:
        return {}, {'user_code': ['Not Acceptable'], }, 406

    elif user_code == user.user_code:
        if os.path.isfile(app.config['QRCODES_PATH'] % user.totp_key):
            os.remove(app.config['QRCODES_PATH'] % user.totp_key)

        user.totp_remains = 0
        db.session.flush()
        db.session.commit()
        cache.set('user.%s' % (user.id), user)
        return {'user_token': user.user_token}, {}, 200

    else:
        user.totp_remains -= 1
        db.session.flush()
        db.session.commit()
        cache.set('user.%s' % (user.id), user)
        return {}, {'user_code': ['Incorrect'], }, 404









def _user_auth(user_token):
    try:
        token_payload = User.get_token_payload(user_token)
    except:
        raise ValidationError({'user_token': ['Incorrect.']})

    user = cache.get('user.%s' % (token_payload['user_id']))
    if not user:
        user = User.query.filter_by(token_signature=token_payload['token_signature'], deleted=0).first()

    if not user:
        raise ValidationError({'user_token': ['Not Found.']})

    #elif user.deleted > 0:
    #    raise ValidationError({'user_token': ['self user deleted.']})
        
    elif user.token_signature != token_payload['token_signature']:
        raise ValidationError({'user_token': ['Not Found.']})

    else:
        cache.set('user.%s' % (user.id), user)
        if user.token_expires < time.time():
            raise ValidationError({'user_token': ['Token Expired.']})
        else:
            return user


@app_response
def _user_signout(user_token):
    authed_user = user_auth(user_token)
    authed_user.token_signature = authed_user.generate_token_signature()
    db.session.flush()
    db.session.commit()
    cache.set('user.%s' % (authed_user.id), authed_user)
    return {}, {}, 200


@app_response
def _user_restore(user_login, user_pass):
    user_login = user_login.lower()
    pass_hash = User.get_pass_hash(user_login + user_pass)
    user = User.query.filter_by(user_login=user_login, deleted=0).first()
    if not user:
        return {}, {'user_login': ['Not Found'], }, 404

    elif user.pass_suspended > time.time():
        return {}, {'user_pass': ['Not Acceptable'], }, 406

    elif user.pass_hash == pass_hash:
        user.pass_remains = PASS_REMAINS_LIMIT
        user.pass_suspended = 0
        user.totp_remains = TOTP_REMAINS_LIMIT
        db.session.flush()
        db.session.commit()
        cache.set('user.%s' % (user.id), user)
        return {}, {}, 200

    else:
        user.pass_remains -= 1
        if user.pass_remains < 1:
            user.pass_remains = PASS_REMAINS_LIMIT
            user.pass_suspended = time.time() + PASS_SUSPENSION_TIME

        db.session.flush()
        db.session.commit()
        cache.set('user.%s' % (user.id), user)
        return {}, {'user_pass': ['Not Found'], }, 404


@app_response
def _user_select(user_token, user_id):
    authed_user = user_auth(user_token)

    user = cache.get('user.%s' % (user_id))
    if not user:
        user = User.query.filter_by(id=user_id).first()

    #has_prop = user.has_prop('key_1')
    #get_prop = user.get_prop('key_1')

    if user:
        cache.set('user.%s' % (user.id), user)
        return {'user': {
            'id': user.id,
            'user_name': user.user_name,
            'props': {prop.prop_key: prop.prop_value for prop in user.props}    
        }}, {}, 200

    else:
        return {}, {'user_id': ['Not Found']}, 404


@app_response
def _user_update(user_token, user_id, user_name=None, user_role=None, user_pass=None, props_data=None):
    authed_user = user_auth(user_token)
    if user_id == authed_user.id:
        user = authed_user

    elif authed_user.is_admin:
        user = cache.get('user.%s' % (user_id))
        if not user:
            user = User.query.filter_by(id=user_id, deleted=0).first()

    else:
        return {}, {'user_id': ['user_id update forbidden'], }, 403

    if not user:
        return {}, {'user_id': ['user_id not found']}, 404

    #elif user.deleted > 0:
    #    return {}, {'user_id': ['user deleted']}, 404

    user_data = {}
    if user_name:
        user_data['user_name'] = user_name

    if user_pass:
        user_data['user_pass'] = user_pass

    if user_role and authed_user.is_admin and authed_user.id != user_id:
        user_data['user_role'] = user_role

    for k in user_data:
        setattr(user, k, user_data[k])
    db.session.add(user)
    db.session.flush()

    if props_data:
        for prop_key in props_data:
            user_prop = UserProp.set_prop(user.id, prop_key, props_data[prop_key])
            db.session.add(user_prop)
        db.session.flush()

    db.session.commit()
    cache.set('user.%s' % (user.id), user)
    return {}, {'user_role:': str({k: user_data[k] for k in user_data}), 'user': str(user)}, 404


@app_response
def _user_delete(user_token, user_id):
    authed_user = user_auth(user_token)
    if user_id == authed_user.id or not authed_user.is_admin:
        return {}, {'user_id': ['Forbidden'], }, 403

    else:
        user = cache.get('user.%s' % (user_id))
        if not user:
            user = User.query.filter_by(id=user_id, deleted=0).first()

    if not user:
        return {}, {'user_id': ['User not found'], }, 404

    user.deleted = time.time()
    db.session.add(user)
    db.session.flush()
    db.session.commit()
    cache.set('user.%s' % (user.id), user)
    return {}, {}, 200
