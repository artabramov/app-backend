from app.core.app_response import app_response
from app import app


@app.route('/api/hi')
@app_response
def hi():
    return {
        'hello': 'hi!',
        'token': 'e9456129-1ead-44cf-aa8c-d49c2719e508',
        'user': {
            'Token': 'e9456129-1ead-44cf-aa8c-d49c2719e508'
        }
    }, {}, 200


