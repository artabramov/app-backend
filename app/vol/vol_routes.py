from flask import request
from app import app
from app.core.app_response import app_response
from app.user.user_handlers import user_auth
from app.vol.vol_handlers import vol_insert, vol_update, vol_select


@app.route('/vol/', methods=['POST'], endpoint='vol_post')
@app_response
def vol_post():
    """ Vol insert """
    user_token = request.headers.get('user_token')
    vol_title = request.args.get('vol_title', None)

    this_user = user_auth(user_token)

    if not this_user.can_edit:
        return {}, {'user_token': ['user_token have not permissions for vol edit'], }, 406

    vol_meta = {
        'key_1': 'value 1',
        'key_2': 'value 2',
        'key_3': 'value 3',
    }

    vol = vol_insert(this_user.id, vol_title, vol_meta)

    return {
        'vol': str(vol)
    }, {}, 201


@app.route('/vol/<vol_id>', methods=['PUT'], endpoint='vol_put')
@app_response
def vol_put(vol_id):
    """ Vol update """
    if not vol_id.isnumeric():
        return {}, {'vol_id': ['vol_id is incorrect']}, 404

    vol_id = int(vol_id)
    user_token = request.headers.get('user_token')
    vol_title = request.args.get('vol_title', None)

    this_user = user_auth(user_token)
    vol = vol_select(id=vol_id)

    if not vol:
        return {}, {'vol_id': ['vol_id not found']}, 404

    elif this_user.can_edit:
        vol_data = {}
        if vol_title:
            vol_data['vol_title'] = vol_title

        vol_data['vol_meta'] = {
            'key_1': 'value 222', 
            'key_2': 'None2',
            'key_3': None,
            'key_4': None}

        vol_update(vol, **vol_data)
        return {}, {}, 200

    else:
        return {}, {'vol_id': ['vol_id update forbidden'], }, 403
