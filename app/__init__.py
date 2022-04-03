from .config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from app.core.app_logger import create_app_logger
from flask_caching import Cache


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

cache = Cache(config={
    'CACHE_TYPE': 'redis',
    'CACHE_DEFAULT_TIMEOUT': 60,
    'CACHE_KEY_PREFIX': '_cached.',
    'CACHE_REDIS_HOST': 'host.docker.internal',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_PASSWORD': '',
    })
cache.init_app(app)

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


@app.before_first_request
def before_first_request():
    from app.user import user_model
    from app.user_meta import user_meta_model
    db.create_all()

    # This code doesn't work in all cases and this functionality
    # has moved to Dockerfile.
    #
    #import os, pwd, grp
    #
    #path = os.path.dirname(app.config['LOG_FILENAME'])
    #if not path.endswith(os.path.sep):
    #    path += os.path.sep
    #
    #if not os.path.isdir(path):
    #    os.mkdir(path)
    #    os.chown(path, uid, gid)
    #
    #if not os.path.isfile(app.config['LOG_FILENAME']):
    #    open(app.config['LOG_FILENAME'], 'a').close()
    #
    #uid = pwd.getpwnam('www-data').pw_uid
    #gid = grp.getgrnam('root').gr_gid
    #for file in os.listdir(path):
    #    os.chown(path + file, uid, gid)


log = create_app_logger(app)

from app.hello.hello_routes import hi
from app.user.user_routes import user_post
from app.user.user_routes import user_get
