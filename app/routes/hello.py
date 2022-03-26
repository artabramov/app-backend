from flask import jsonify
from app import app


@app.route('/hi/')
def hi():
    return jsonify({"hello": "hi!"})


