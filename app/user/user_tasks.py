from app import db, log, celery
from app.user.user_model import UserModel
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

#source /app/venv/bin/activate && celery -A app.core.worker.celery worker --loglevel=info

@celery.task(name='app.user_insert', time_limit=10, ignore_result=False)
def user_insert(user_email, user_pass, user_name):

    try:
        user = UserModel(user_email, user_pass, user_name)
        db.session.add(user)
        db.session.flush()
        db.session.commit()
        return {'user': {'id': user.id}}, {}, 201

    except ValidationError as e:
        log.debug(e.messages)
        db.session.rollback()
        return {}, e.messages, 400

    except SQLAlchemyError as e:
        log.error(e.orig.msg)
        db.session.rollback()
        return {}, {'db': ['Internal Server Error']}, 500

    except Exception as e:
        log.error(e)
        db.session.rollback()
        return {}, {'db': ['Internal Server Error']}, 500
