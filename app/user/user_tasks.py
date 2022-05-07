from app import app, db, celery, cache
from app.user.user_schema import UserSchema
from app.user.user_model import UserModel
from app.user_meta.user_meta_schema import UserMetaSchema
from app.user_meta.user_meta_model import UserMetaModel
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from celery.utils.log import get_task_logger
import time
from app.user.user_model import PASS_ATTEMPTS_LIMIT, PASS_SUSPENSION_TIME, CODE_ATTEMPTS_LIMIT
from app.user.user_helpers import user_auth
from app.user.user_schema import UserRole
import qrcode
import os
from werkzeug.utils import secure_filename
import uuid

log = get_task_logger(__name__)


@celery.task(name='app.user_register', time_limit=10, ignore_result=False)
def user_register(user_login, user_name, user_pass, meta_data=None):
    try:
        UserSchema().load({'user_login': user_login, 'user_name': user_name, 'user_pass': user_pass})
        user = UserModel(user_login, user_name, user_pass)
        db.session.add(user)
        db.session.flush()
        user.user_role = UserRole.admin if user.id == 1 else UserRole.newbie

        if meta_data:
            for meta_key in meta_data:
                meta_value = meta_data[meta_key]
                UserMetaSchema().load({
                    'user_id': user.id,
                    'meta_key': meta_key,
                    'meta_value': meta_value,
                })
                user_meta = UserMetaModel(user.id, meta_key, meta_value)
                db.session.add(user_meta)
            db.session.flush()

        qr = qrcode.make(app.config['QR_LINK_MASK'] % (user.code_secret, user.user_login))
        qr.save(app.config['QR_PATH_MASK'] % user.code_secret)

        db.session.commit()
        cache.set('user.%s' % (user.id), user)
        return {
            'code_secret': user.code_secret, 
            'code_qr': app.config['QR_URI_MASK'] % user.code_secret
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


@celery.task(name='app.user_restore', time_limit=10, ignore_result=False)
def user_restore(user_login, user_pass):
    try:
        user_login = user_login.lower()
        pass_hash = UserModel.get_pass_hash(user_login + user_pass)
        user = UserModel.query.filter_by(user_login=user_login, deleted=0).first()
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

    except SQLAlchemyError as e:
        log.error(e)
        db.session.rollback()
        return {}, {'error': ['Service Unavailable']}, 503

    except Exception as e:
        log.error(e)
        db.session.rollback()
        return {}, {'error': ['Internal Server Error']}, 500


@celery.task(name='app.user_login', time_limit=10, ignore_result=False)
def user_signin(user_login, user_code):
    try:
        UserSchema().load({'user_login': user_login, 'user_code': user_code})
        user = UserModel.query.filter_by(user_login=user_login, deleted=0).first()
        
        if not user:
            return {}, {'user_login': ['Not Found'], }, 404
        
        elif user.code_attempts < 1:
            return {}, {'user_code': ['Not Acceptable'], }, 406

        elif user_code == user.get_code_value():
            if os.path.isfile(app.config['QR_PATH_MASK'] % user.code_secret):
                os.remove(app.config['QR_PATH_MASK'] % user.code_secret)

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
        return {}, {'error': ['Internal Server Error']}, 500


@celery.task(name='app.user_logout', time_limit=10, ignore_result=False)
def user_signout(user_token):
    try:
        authed_user = user_auth(user_token)
        authed_user.set_token_signature()
        db.session.flush()
        db.session.commit()
        return {}, {}, 200

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
        return {}, {'error': ['Internal Server Error']}, 500


@celery.task(name='app.user_select', time_limit=10, ignore_result=False)
def user_select(user_token, user_id):
    try:
        authed_user = user_auth(user_token)

        user = cache.get('user.%s' % (user_id))
        if not user:
            user = UserModel.query.filter_by(id=user_id).first()

        if user:
            cache.set('user.%s' % (user.id), user)
            return {'user': {
                'id': user.id,
                'user_name': user.user_name,
                'user_meta': {meta.meta_key: meta.meta_value for meta in user.user_meta}    
            }}, {}, 200
        else:
            return {}, {'user_id': ['Not Found']}, 404

    except ValidationError as e:
        log.debug(e.messages)
        db.session.rollback()
        return {}, e.messages, 400

    except SQLAlchemyError as e:
        log.error(e)
        return {}, {'error': ['Service Unavailable']}, 503

    except Exception as e:
        log.error(e)
        return {}, {'error': ['Internal Server Error']}, 500


@celery.task(name='app.user_update', time_limit=10, ignore_result=False)
def user_update(user_token, user_id, user_name=None, user_role=None, user_pass=None, meta_data=None):
    try:
        authed_user = user_auth(user_token)
        if user_id == authed_user.id:
            user = authed_user

        elif authed_user.user_role == UserRole.admin:
            user = cache.get('user.%s' % (user_id))
            if not user:
                user = UserModel.query.filter_by(id=user_id, deleted=0).first()

        else:
            return {}, {'user_id': ['Forbidden'], }, 403

        user_data = {}
        if user_name and authed_user.id == user_id:
            user_data['user_name'] = user_name

        if user_role and authed_user.user_role == UserRole.admin and authed_user.id != user_id:
            user_data['user_role'] = UserRole.get_role(user_role)

        if user_pass and authed_user.id == user_id:
            user_data['user_pass'] = user_pass

        UserSchema().load(user_data)

        for k in user_data:
            setattr(user, k, user_data[k])

        db.session.add(user)
        db.session.flush()

        if meta_data:
            for meta_key in meta_data:
                meta_value = meta_data[meta_key]
                UserMetaSchema().load({
                    'user_id': user.id,
                    'meta_key': meta_key,
                    'meta_value': meta_value,
                })

                user_meta = UserMetaModel.query.filter_by(user_id=user_id, meta_key=meta_key).first()
                if user_meta:
                    user_meta.meta_value = meta_value
                else:
                    user_meta = UserMetaModel(user_id, meta_key, meta_value)
                db.session.add(user_meta)
            db.session.flush()

        db.session.commit()
        cache.set('user.%s' % (user.id), user)
        return {}, {'user_role:': str({k: user_data[k] for k in user_data}), 'user': str(user)}, 404

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
        return {}, {'error': ['Internal Server Error!']}, 500


@celery.task(name='app.user_delete', time_limit=10, ignore_result=False)
def user_remove(user_token, user_id):
    try:
        authed_user = user_auth(user_token)
        if user_id == authed_user.id or authed_user.user_role != UserRole.admin:
            return {}, {'user_id': ['Forbidden'], }, 403

        else:
            user = cache.get('user.%s' % (user_id))
            if not user:
                user = UserModel.query.filter_by(id=user_id, deleted=0).first()

        if not user:
            return {}, {'user_id': ['Not Found'], }, 404

        user.deleted = time.time()
        db.session.add(user)
        db.session.flush()
        db.session.commit()
        cache.set('user.%s' % (user.id), user)
        return {}, {}, 200

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
        return {}, {'error': ['Internal Server Error!']}, 500


@celery.task(name='app.image_upload', time_limit=10, ignore_result=False)
def image_upload(user_token, file_data, tmp):
    try:
        authed_user = user_auth(user_token)
        meta_key = 'user_image'
        meta_value = file_data['filename_dst']

        user_meta = UserMetaModel.query.filter_by(user_id=authed_user.id, meta_key=meta_key).first()
        if user_meta:
            if os.path.isfile(user_meta.meta_value):
                os.remove(user_meta.meta_value)
            user_meta.meta_value = meta_value
        else:
            user_meta = UserMetaModel(authed_user.id, meta_key, meta_value)
        db.session.add(user_meta)
        db.session.flush()

        db.session.commit()
        cache.set('user.%s' % (authed_user.id), authed_user)
        return {}, {}, 200

    except ValidationError as e:
        log.debug(e.messages)
        db.session.rollback()
        return {}, e.messages, 400

    except SQLAlchemyError as e:
        log.error(e)
        return {}, {'error': ['Service Unavailable']}, 503

    except Exception as e:
        log.error(e)
        return {}, {'error': ['Internal Server Error']}, 500
