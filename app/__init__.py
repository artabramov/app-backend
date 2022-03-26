"""
from .config import Config
from flask import Flask
import connexion

connexion_app = connexion.FlaskApp(__name__, specification_dir='./')
connexion_app.add_api('swagger.yml')

app = connexion_app.app
app.config.from_object(Config)
"""

from .config import Config
from flask import Flask

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/hi')
def hi():
    return 'hi2!'
