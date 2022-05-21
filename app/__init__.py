from .config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.core.app_logger import create_logger
from flask_caching import Cache


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

cache = Cache(config={
    'CACHE_TYPE': 'redis',
    'CACHE_DEFAULT_TIMEOUT': 60 * 5,
    'CACHE_KEY_PREFIX': 'cache.',
    'CACHE_REDIS_HOST': 'host.docker.internal',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_PASSWORD': '',
    })
cache.init_app(app)
cache.set('a', 'A')


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


log = create_logger(app)

from app.hello.hello_routes import hi
from app.user.user_routes import user_register
#from app.user.user_routes import pass_get
#from app.user.user_routes import token_get
#from app.user.user_routes import token_put
#from app.user.user_routes import user_get
#from app.user.user_routes import user_put
#from app.user.user_routes import image_post
