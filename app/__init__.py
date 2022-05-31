from .config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.core.app_logger import create_logger
from flask_caching import Cache


app = Flask(__name__)
app.config.from_object(Config)

log = create_logger(app)

db = SQLAlchemy(app)

cache = Cache(config=app.config)
cache.init_app(app)


@app.before_first_request
def before_first_request():
    from app.user import user
    from app.user import user_meta
    from app.vol import vol, vol_meta
    db.create_all()


from app.hi import hi_routes
from app.user import user_routes
from app.vol import vol_routes
