from .config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from app.core.logger import create_logger

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

celery = Celery(
    broker=app.config['CELERY_BROKER_URL'],
    backend=app.config['CELERY_RESULT_BACKEND'],
    include=app.config['CELERY_TASK_LIST'],
)
celery.conf.task_routes = app.config['CELERY_TASK_ROUTES']
celery.conf.result_expires = app.config['CELERY_RESULT_EXPIRES']

log = create_logger(app)

from app.hello.hello_routes import hi
from app.user.user_routes import user_post
from app.user.user_routes import user_get

from app.user import user_model
db.create_all()




