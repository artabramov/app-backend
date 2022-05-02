from app import db, celery, cache
from app.user.user_model import UserModel
from app.user_meta.user_meta_model import UserMetaModel
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from celery.utils.log import get_task_logger
import time
from app.user.user_model import PASS_ATTEMPTS_LIMIT, PASS_SUSPENSION_TIME, CODE_ATTEMPTS_LIMIT
from app.user.user_helpers import user_auth
from app.user.user_schema import UserRole
import pyotp

log = get_task_logger(__name__)


@celery.task(name='app.user_register', time_limit=10, ignore_result=False)
def user_register(user_login, user_name, user_pass):
    try:
        user = UserModel(user_login, user_name, user_pass)
        user.user_role = UserRole.admin if user.id == 1 else UserRole.nobody
        db.session.add(user)
        db.session.flush()

        user_meta = UserMetaModel(user.id, 'key', 'value')
        db.session.add(user_meta)
        db.session.flush()

        db.session.commit()

        cache.set('user.%s' % (user.id), user)
        return {'code_secret': user.code_secret}, {}, 201

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
            return {}, {'user_pass': ['Suspended'], }, 404

        elif user.pass_hash == pass_hash:
            user.pass_attempts = 0
            user.pass_suspended = 0
            user.code_attempts = 0
            db.session.flush()
            db.session.commit()
            cache.set('user.%s' % (user.id), user)
            return {}, {}, 200

        else:
            user.pass_attempts += 1
            if user.pass_attempts >= PASS_ATTEMPTS_LIMIT:
                user.pass_attempts = 0
                user.pass_suspended = time.time() + PASS_SUSPENSION_TIME

            db.session.flush()
            db.session.commit()
            cache.set('user.%s' % (user.id), user)
            return {}, {'user_pass': ['Incorrect'], }, 404

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
        user = UserModel.query.filter_by(user_login=user_login, deleted=0).first()
        #return {'user_totp': user.totp(), }, {}, 404
        totp = pyotp.TOTP(user.code_secret)
        return {
            'code_secret': str(user.code_secret),
            'user_totp': totp.now(),
        }, {}, 404

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
        authed_user.update_signature()
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
        db.session.rollback()
        return {}, {'error': ['Service Unavailable']}, 503

    except Exception as e:
        log.error(e)
        return {}, {'error': ['Internal Server Error']}, 500


@celery.task(name='app.user_select', time_limit=10, ignore_result=False)
def user_select(user_token, user_id):
    try:
        authed_user = user_auth(user_token)
        cache.set('user.%s' % (authed_user.id), authed_user)

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

    except SQLAlchemyError as e:
        log.error(e)
        return {}, {'error': ['Service Unavailable']}, 503

    except Exception as e:
        log.error(e)
        return {}, {'error': ['Internal Server Error']}, 500


@celery.task(name='app.user_update', time_limit=10, ignore_result=False)
def user_update(user_token, user_id, user_name, is_admin=None, deleted=None):
    try:
        authed_user = user_auth(user_token)
        cache.set('user.%s' % (authed_user.id), authed_user)

        user = None
        if authed_user.id == user_id:
            user = authed_user

        elif authed_user.is_admin:
            user = cache.get('user.%s' % (user_id))
            if not user:
                user = UserModel.query.filter_by(id=user_id).first()

        else:
            return {}, {'user_id': ['Forbidden'], }, 403

        if not user:
            return {}, {'user_id': ['Not Found'], }, 404

        if user_name:
            user.user_name = user_name

        if authed_user.is_admin and isinstance(is_admin, bool):
            user.is_admin = is_admin

        db.session.add(user)
        db.session.flush()
        db.session.commit()
        cache.set('user.%s' % (user.id), user)

        return {}, {'wtf:': ['Whoah!'], }, 404

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
