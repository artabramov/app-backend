from app import db, log, celery
from app.user.user_model import UserModel
from app.user_meta.user_meta_model import UserMetaModel
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from app import cache

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
        log.warning(e.messages)
        db.session.rollback()
        return {}, e.messages, 400

    except SQLAlchemyError as e:
        log.critical(e)
        db.session.rollback()
        return {}, {'error': ['Service Unavailable']}, 503

    except Exception as e:
        log.critical(e)
        db.session.rollback()
        return {}, {'error': ['Internal Server Error']}, 500


@celery.task(name='app.user_select', time_limit=10, ignore_result=False)
def user_select(user_id):
    try:
        user = UserModel.query.filter_by(id=user_id).first()
        if user:
            cache.set('user(id=%s)' % (user_id), user)
            return {'user': {
                'id': user.id,
                'user_name': user.user_name,
            }}, {}, 200
        else:
            return {}, {'user_id': ['Not Found']}, 404

    except ValidationError as e:
        log.warning(e.messages)
        return {}, e.messages, 400

    except SQLAlchemyError as e:
        log.critical(e)
        return {}, {'error': ['Service Unavailable']}, 503

    except Exception as e:
        log.critical(e)
        return {}, {'error': ['Internal Server Error']}, 500
