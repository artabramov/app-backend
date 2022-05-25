from app.core.json_response import make_json
from app import app


@app.route('/hi')
def hi():
    return make_json({
        'hello': 'hi!',
        'token': 'e9456129-1ead-44cf-aa8c-d49c2719e508',
        'user': {
            'Token': 'e9456129-1ead-44cf-aa8c-d49c2719e508'
        }
    })


