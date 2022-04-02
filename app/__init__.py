from .config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from app.core.logger import create_logger
import os, pwd, grp
from app.user import user_model


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)


def make_celery():
    celery = Celery(
        broker=app.config['CELERY_BROKER_URI'],
        backend=app.config['CELERY_BACKEND_URI'],
        include=app.config['CELERY_TASKS_LIST'],
    )
    celery.conf.task_routes = app.config['CELERY_ROUTING_KEYS']
    celery.conf.result_expires = app.config['CELERY_RESULT_EXPIRES']
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery
celery = make_celery()

@app.before_request
def before_request():
    if not os.path.isfile(app.config['LOG_FILENAME']):
        open(app.config['LOG_FILENAME'], 'a').close()

    uid = pwd.getpwnam('www-data').pw_uid
    gid = grp.getgrnam('root').gr_gid
    for file in os.path.dirname(app.config['LOG_FILENAME']):
        os.chown(file, uid, gid)

    db.create_all()

log = create_logger(app)

from app.hello.hello_routes import hi
from app.user.user_routes import user_post
from app.user.user_routes import user_get






