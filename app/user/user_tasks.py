from app import db, celery, cache
from app.user.user_model import UserModel
from app.user_meta.user_meta_model import UserMetaModel
#from app.core.task_logger import create_logger
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
#log = create_logger(__name__)

from celery.utils.log import get_task_logger
log = get_task_logger(__name__)

    

#source /app/venv/bin/activate && celery -A app.core.worker.celery worker --loglevel=info

@celery.task(name='app.user_insert', time_limit=10, ignore_result=False)
def user_insert(user_email, user_pass, user_name):
    try:
        user = UserModel(user_email, user_pass, user_name)
        db.session.add(user)
        db.session.flush()

        user_meta = UserMetaModel(user.id, 'key', 'value')
        db.session.add(user_meta)
        db.session.flush()

        db.session.commit()
        return {'user': {
            'id': user.id,
            'user_name': user.user_name
            }}, {}, 201

    except ValidationError as e:
        log.error('e.messages')
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


@celery.task(name='app.user_select', time_limit=10, ignore_result=False)
def user_select(user_id):
    try:
        user = UserModel.query.filter_by(id=user_id).first()
        log.debug('task debug')

        if user:
            cache.set('user.%s' % (user_id), user)
            return {'user': {
                'id': user.id,
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
