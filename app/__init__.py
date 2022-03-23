from flask import Flask
from .config import Config

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/api/hello/')
def hello():
    return 'hello'
