from .config import Config
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from app.core.app_logger import create_logger
from app.core.app_errors import create_errors
from flask_caching import Cache
import os


app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

log = create_logger(app)
err = create_errors()

db = SQLAlchemy(app)

cache = Cache(config=app.config)
cache.init_app(app)


@app.before_first_request
def before_first_request():
    from app.models import user, user_meta, volume, volume_meta, category, post, post_meta, post_tag, comment, upload
    db.create_all()


from app.routes import user_routes, volume_routes, category_routes, post_routes, comment_routes, upload_routes, hi_routes



