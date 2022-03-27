from .config import Config
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from app.core.create_logger import create_logger

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

log = create_logger(app)

from app.routes.hello import hi
from app.routes.user import user_post

from app.models import user
db.create_all()




