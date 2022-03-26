from flask import jsonify
from app import app, log


@app.route('/hi/')
def hi():
    log.error('hi error')
    return jsonify({"hello": "hi!"})


