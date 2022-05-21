from app.core.json_response import json_response
from app import app


@app.route('/hi')
def hi():
    return json_response({
        'hello': 'hi!',
        'token': 'e9456129-1ead-44cf-aa8c-d49c2719e508',
        'user': {
            'Token': 'e9456129-1ead-44cf-aa8c-d49c2719e508'
        }
    })


