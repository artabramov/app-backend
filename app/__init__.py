from .config import Config
from flask import Flask
from app.core.logger import logger

app = Flask(__name__)
app.config.from_object(Config)

log = logger(app)

from app.routes.hello import hi




