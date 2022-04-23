from app import db, celery, cache
from app.user.user_model import UserModel
from app.user_meta.user_meta_model import UserMetaModel
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from celery.utils.log import get_task_logger
from logging import Logger
import time
from app.user.user_model import PASS_EXPIRATION_TIME, PASS_ATTEMPTS_LIMIT

log = get_task_logger(__name__)


@celery.task(name='app.user_register', time_limit=10, ignore_result=False)
def user_register(user_email, user_name):
    try:
        user = UserModel(user_email, user_name)
        #user.user_token = user.create_token()
        #user.user_pass = user.create_pass()
        db.session.add(user)
        db.session.flush()

        user_meta = UserMetaModel(user.id, 'key', 'value')
        db.session.add(user_meta)
        db.session.flush()

        db.session.commit()

        

        # TODO: send user_pass to email
        log.info("user_email: %s, user_pass: %s" % (user.user_email, user.user_pass))
        return {'user': {'id': user.id}}, {}, 201

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


@celery.task(name='app.user_login', time_limit=10, ignore_result=False)
def user_login(user_email, user_pass):
    try:
        #pass_hash = UserModel.get_hash(user_email.lower() + user_pass)
        user = UserModel.query.filter_by(user_email=user_email, deleted=0).first()

        if not user:
            return {}, {'user_email': ['Not Found'], }, 404

        elif user.pass_expires < time.time():
            return {}, {'user_pass': ['Pass Expired'], }, 404

        elif user.pass_attempts >= PASS_ATTEMPTS_LIMIT - 1:
            return {}, {'user_pass': ['Attempts Limit'], }, 404

        elif user.pass_hash != UserModel.get_hash(user_email.lower() + user_pass):
            user.pass_attempts += 1
            db.session.flush()
            db.session.commit()
            return {}, {'user_pass': ['Incorrect'], }, 404

        else:
            user.pass_expires = 0
            user.pass_attempts = 0
            db.session.flush()
            db.session.commit()
            cache.set('user.%s' % (user.id), user)
            return {'user': {'id': user.id, 'user_token': user.user_token}}, {}, 201

    except SQLAlchemyError as e:
        log.error(e)
        db.session.rollback()
        return {}, {'error': ['Service Unavailable']}, 503

    except Exception as e:
        log.error(e)
        return {}, {'error': ['Internal Server Error']}, 500

"""
@celery.task(name='app.user_restore', time_limit=10, ignore_result=False)
def user_restore(user_email, user_pass):
    try:
        pass_hash = UserModel.get_hash(user_email.lower() + user_pass)
        user = UserModel.query.filter_by(user_email=user_email, pass_hash=pass_hash, deleted_at=0).first()

        if not user:
            return {}, {'user_email': ['Incorrect Credentials'], }, 404

        elif user.lockout_to > time.time():
            return {}, {'user_email': ['Temporary Lockout'], }, 404

        else:
            user.update_code()
            db.session.add(user)
            db.session.flush()
            db.session.commit()

            cache.set('user.%s' % (user.id), user)

            # TODO: send confirm_code to email
            return {'user': {'id': user.id}}, {}, 201

    except SQLAlchemyError as e:
        log.error(e)
        return {}, {'error': ['Service Unavailable']}, 503

    except Exception as e:
        log.error(e)
        return {}, {'error': ['Internal Server Error']}, 500


@celery.task(name='app.user_restore', time_limit=10, ignore_result=False)
def user_restore(user_id, confirm_code):
    try:
        pass_hash = UserModel.get_hash(user_email.lower() + user_pass)
        user = UserModel.query.filter_by(user_email=user_email, pass_hash=pass_hash, deleted_at=0).first()

        if not user:
            return {}, {'user_email': ['Incorrect Credentials'], }, 404

        elif user.lockout_to > time.time():
            return {}, {'user_email': ['Temporary Lockout'], }, 404

        else:
            cache.set('user.%s' % (user.id), user)
            return {'user': {
                'id': user.id,
                'deleted_at': user.deleted_at,
                'user_status': user.user_status.name,
                'user_name': user.user_name,
            }}, {}, 200

    except ValidationError as e:
        log.debug(e.messages)
        return {}, e.messages, 400

    except SQLAlchemyError as e:
        log.error(e)
        return {}, {'error': ['Service Unavailable']}, 503

    except Exception as e:
        log.error(e)
        return {}, {'error': ['Internal Server Error']}, 500
"""






@celery.task(name='app.user_select', time_limit=10, ignore_result=False)
def user_select(user_id):
    try:
        user = UserModel.query.filter_by(id=user_id).first()
        log.debug('task debug')

        if user:
            cache.set('user.%s' % (user.id), user)
            return {'user': {
                'id': user.id,
                'user_status': user.user_status.name,
                'user_name': user.user_name,
            }}, {}, 200
        else:
            return {}, {'user_id': ['Not Found']}, 404

    except ValidationError as e:
        log.debug(e.messages)
        return {}, e.messages, 400

    except SQLAlchemyError as e:
        log.error(e)
        return {}, {'error': ['Service Unavailable']}, 503

    except Exception as e:
        log.error(e)
        return {}, {'error': ['Internal Server Error']}, 500
