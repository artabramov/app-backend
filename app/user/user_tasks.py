from app import celery

#source /app/venv/bin/activate && celery -A app.core.worker.celery worker --loglevel=info

@celery.task(name='app.user_insert', time_limit=10, ignore_result=False)
def user_insert(user_email, user_password, user_name):
    return {'key': 'value'}, {}, 201
