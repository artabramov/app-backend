from .config import Config
from flask import Flask

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/hi')
#@swag_from('swagger.yml')
def hi():
    return 'hi2!'

