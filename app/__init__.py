from .config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.core.logger import create_logger

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

log = create_logger(app)

from app.hello.hello_routes import hi
from app.user.user_routes import user_post
from app.user.user_routes import user_get

from app.user import user_model
db.create_all()




