from .config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from app.core.logger import create_logger
#import os, pwd, grp


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)


def make_celery():
    celery = Celery(
        'tasks',
        broker='redis://host.docker.internal:6379/0',
        backend='redis://host.docker.internal:6379/1'
    )
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery
celery = make_celery()


if not os.path.isfile(app.config['LOG_FILENAME']):
    uid = pwd.getpwnam('www-data').pw_uid
    gid = grp.getgrnam('root').gr_gid
    open(app.config['LOG_FILENAME'], 'a').close()
    os.chown(app.config['LOG_FILENAME'], uid, gid)
log = create_logger(app)

from app.hello.hello_routes import hi
from app.user.user_routes import user_post
from app.user.user_routes import user_get

from app.user import user_model
db.create_all()




