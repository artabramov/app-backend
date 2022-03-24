from .config import Config
from flask import Flask
import connexion

connexion_app = connexion.App(__name__, specification_dir='./')
connexion_app.add_api('swagger.yml')

app = connexion_app.app
app.config.from_object(Config)

tmp = 1

@app.before_first_request
def create_tables():
    #db.create_all()
    pass

@app.before_request
def asdfasfd():
    pass
