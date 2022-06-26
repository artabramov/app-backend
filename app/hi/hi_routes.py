from app.core.app_response import app_response
from app import app


@app.route('/hi')
@app_response
def hi1():
    return {
        'hello': 'hi1',
        'token': 'e9456129-1ead-44cf-aa8c-d49c2719e508',
        'user': {
            'Token': 'e9456129-1ead-44cf-aa8c-d49c2719e508'
        }
    }, {}, 200


@app.route('/api/hi')
@app_response
def hi2():
    return {
        'hello': 'hi2',
        'token': 'e9456129-1ead-44cf-aa8c-d49c2719e508',
        'user': {
            'Token': 'e9456129-1ead-44cf-aa8c-d49c2719e508'
        }
    }, {}, 200
