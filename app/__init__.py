from .config import Config
from flask import Flask


#from core.connexion import ConnexionApp
#connexion_app = ConnexionApp(__name__, specification_dir='./')
#connexion_app.creare_api('swagger.yml', api_name='asdads')

"""
import connexion
connexion_app = connexion.FlaskApp(__name__, specification_dir='./')
connexion_app.add_api('swagger.yml')

app = connexion_app.app
app.config.from_object(Config)

@app.before_request
def before_request():
    print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
"""



app = Flask(__name__)
app.config.from_object(Config)

@app.before_request
def before_request():
    print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')

@app.route('/hi')
def qwer():
    return 'flask!'


a = 1
