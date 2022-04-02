from .config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from app.core.logger import create_logger
import os, pwd, grp


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
    from app.user import user_model
    db.create_all()

    uid = pwd.getpwnam('www-data').pw_uid
    gid = grp.getgrnam('root').gr_gid

    path = os.path.dirname(app.config['LOG_FILENAME'])
    if not path.endswith(os.path.sep):
        path += os.path.sep

    if not os.path.isdir(path):
        os.mkdir(path)
        os.chown(path, uid, gid)

    if not os.path.isfile(app.config['LOG_FILENAME']):
        open(app.config['LOG_FILENAME'], 'a').close()

    for file in os.listdir(path):
        os.chown(path + file, uid, gid)


log = create_logger(app)

from app.hello.hello_routes import hi
from app.user.user_routes import user_post
from app.user.user_routes import user_get
