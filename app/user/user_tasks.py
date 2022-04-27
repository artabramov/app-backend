from app import db, celery, cache
from app.user.user_model import UserModel
from app.user_meta.user_meta_model import UserMetaModel
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from celery.utils.log import get_task_logger
import time
from app.user.user_model import PASS_ATTEMPTS_LIMIT

log = get_task_logger(__name__)


@celery.task(name='app.user_register', time_limit=10, ignore_result=False)
def user_register(user_email, user_name):
    try:
        user = UserModel(user_email, user_name)
        db.session.add(user)
        db.session.flush()

        user_meta = UserMetaModel(user.id, 'key', 'value')
        db.session.add(user_meta)
        db.session.flush()

        db.session.commit()

        if user.id == 1:
            user.is_admin = True
            db.session.flush()
            db.session.commit()

        cache.set('user.%s' % (user.id), user)

        # TODO: send user_pass to email
        log.info("REGISTER user_email: %s, user_pass: %s" % (user.user_email, user.user_pass))
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


@celery.task(name='app.user_restore', time_limit=10, ignore_result=False)
def user_restore(user_email):
    try:
        user = UserModel.query.filter_by(user_email=user_email, deleted=0).first()

        if not user:
            return {}, {'user_email': ['Not Found'], }, 404

        elif user.pass_expires > time.time():
            return {}, {'user_email': ['Wait a Bit'], }, 404

        else:
            user.update_pass()
            db.session.add(user)
            db.session.flush()
            db.session.commit()
            cache.set('user.%s' % (user.id), user)

            # TODO: send user_pass to email
            log.info("RESTORE user_email: %s, user_pass: %s" % (user.user_email, user.user_pass))
            return {'user': {'id': user.id}}, {}, 201

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
        user = UserModel.query.filter_by(user_email=user_email, deleted=0).first()

        if not user:
            return {}, {'user_email': ['Not Found'], }, 404

        elif user.pass_expires < time.time():
            return {}, {'user_pass': ['Pass Expired'], }, 404

        elif user.pass_attempts >= PASS_ATTEMPTS_LIMIT:
            return {}, {'user_pass': ['Attempts Limit'], }, 404

        elif user.pass_hash != UserModel.get_hash(user_email.lower() + user_pass):
            user.pass_attempts += 1
            db.session.flush()
            db.session.commit()
            cache.set('user.%s' % (user.id), user)
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


@celery.task(name='app.user_logout', time_limit=10, ignore_result=False)
def user_logout(user_token):
    try:
        authed_user = UserModel.query.filter_by(user_token=user_token, deleted=0).first()
        if not authed_user:
            return {}, {'user_token': ['Not Found'], }, 404

        authed_user.update_token()
        db.session.flush()
        db.session.commit()
        cache.set('user.%s' % (authed_user.id), authed_user)
        return {}, {}, 200

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
        authed_user = UserModel.query.filter_by(user_token=user_token, deleted=0).first()
        if not authed_user:
            return {}, {'user_token': ['Not Found'], }, 404
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
        authed_user = UserModel.query.filter_by(user_token=user_token, deleted=0).first()
        if not authed_user:
            return {}, {'user_token': ['Not Found'], }, 404
        cache.set('user.%s' % (authed_user.id), authed_user)

        user = None
        if authed_user.id == user_id:
            user = authed_user
        elif authed_user.id != user_id  and authed_user.is_admin == True:
            user = cache.get('user.%s' % (user_id))
            if not user:
                user = UserModel.query.filter_by(id=user_id).first()
        
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
