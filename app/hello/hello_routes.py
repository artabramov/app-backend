from app.core.response import response
from app import app


@app.route('/hi')
def hi():
    return response({
        'hello': 'hi!',
        'token': 'e9456129-1ead-44cf-aa8c-d49c2719e508',
        'user': {
            'Token': 'e9456129-1ead-44cf-aa8c-d49c2719e508'
        }
    })


