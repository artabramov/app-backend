from flask import request
from app import app
from app.core.app_response import app_response
from app.user.user_handlers import user_auth
from app.vol.vol_handlers import vol_insert


@app.route('/vol/', methods=['POST'], endpoint='vol_post')
@app_response
def vol_post():
    """ Vol insert """
    user_token = request.headers.get('user_token')
    vol_title = request.args.get('vol_title', None)

    this_user = user_auth(user_token)

    if not this_user.can_edit:
        return {}, {'user_token': ['user_token have not permissions for edit'], }, 406

    vol_meta = {
        'key_1': 'value 1',
        'key_2': 'value 2',
        'key_3': 'value 3',
    }

    vol = vol_insert(this_user.id, vol_title, vol_meta)

    return {
        'vol': str(vol)
    }, {}, 201

