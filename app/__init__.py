from flask import Flask
import connexion

connexion_app = connexion.App(__name__, specification_dir='./')
connexion_app.add_api('swagger.yml')
app = connexion_app.app

#flask_app = Flask(__name__)
#@flask_app.route('/hello')
#def hello():
#    return 'hello'
