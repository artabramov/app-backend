from app import app, celery
from app.core.response import response

#source /app/venv/bin/activate && celery -A app.user.user_workers.celery worker --loglevel=info

@celery.task(name='app.user_insert', time_limit=10, ignore_result=False)
def user_insert(user_email, user_password, user_name):
    return response({'key': 'value'}, {}, 201)
