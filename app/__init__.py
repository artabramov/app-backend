from .config import Config
from flask import Flask, request
from app.core.create_logger import create_logger

app = Flask(__name__)
app.config.from_object(Config)

log = create_logger(app)

from app.routes.hello import hi







