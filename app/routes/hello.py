from flask import jsonify
from app import app, log


@app.route('/hi/')
def hi():
    log.error('hi error')
    return jsonify({
        'hello': 'hi!',
        'token': 'e9456129-1ead-44cf-aa8c-d49c2719e508',
        'user': {
            'Token': 'e9456129-1ead-44cf-aa8c-d49c2719e508'
        }
    })


