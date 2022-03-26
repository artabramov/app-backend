from .config import Config
from flask import Flask
import connexion

connexion_app = connexion.FlaskApp(__name__, specification_dir='./')
connexion_app.add_api('swagger.yml')

app = connexion_app.app
app.config.from_object(Config)
