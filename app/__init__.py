from flask import Flask
import connexion

app = connexion.App(__name__, specification_dir='./')
app.add_api('openapi.yml')
#app = Flask(__name__)

#@app.route('/')
def hello():
    return 'hello2'
