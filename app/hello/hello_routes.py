from app.core.json_response import json_response
from app import app, cache
from app.user.user_model import UserModel
from sqlalchemy.orm import lazyload


@app.route('/hi')
def hi():
    #user = UserModel.query.filter_by(id=1).first()
    #cache.set('user.1', user)
    #user = cache.get('user.1')

    return json_response({
        'hello': 'hi!',
        'token': 'e9456129-1ead-44cf-aa8c-d49c2719e508',
        'user': {
            'Token': 'e9456129-1ead-44cf-aa8c-d49c2719e508'
        }
    })


