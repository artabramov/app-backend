from flask import request
from app import app
from app.core.app_response import app_response
from app.user.user_handlers import user_auth
from app.core.primary_handlers import insert, update, delete, select, search
from app.vol.vol import Vol


@app.route('/vol/', methods=['POST'], endpoint='vol_post')
@app_response
def vol_post():
    """ Volume insert """
    user_token = request.headers.get('user_token', None)
    vol_title = request.args.get('vol_title', None)
    vol_currency = request.args.get('vol_currency', None)

    this_user = user_auth(user_token)

    if not this_user.can_edit:
        return {}, {'user_token': ['user_token have not permissions for vol edit'], }, 406

    vol_meta = {
        'key_1': 'value 1!!!',
        'key_2': 'value 2!!!',
        'key_3': 'value 3!!!',
    }

    vol = insert(Vol, user_id=this_user.id, vol_title=vol_title, vol_currency=vol_currency, meta=vol_meta)

    return {
        'vol': str(vol)
    }, {}, 201


@app.route('/vol/<vol_id>', methods=['PUT'], endpoint='vol_put')
@app_response
def vol_put(vol_id):
    """ Volume update """
    if not vol_id.isnumeric():
        return {}, {'vol_id': ['vol_id is incorrect']}, 404

    vol_id = int(vol_id)
    user_token = request.headers.get('user_token')
    vol_title = request.args.get('vol_title', None)
    vol_currency = request.args.get('vol_currency', None)

    this_user = user_auth(user_token)
    vol = select(Vol, id=vol_id)

    if not vol:
        return {}, {'vol_id': ['vol_id not found']}, 404

    elif this_user.can_edit:
        vol_data = {}
        if vol_title:
            vol_data['vol_title'] = vol_title
        if vol_currency:
            vol_data['vol_currency'] = vol_currency

        vol_data['meta'] = {
            'key_1': '444444444444444444444444444444444', 
            'key_2': '222-222-333',
            'key_3': None,
            'key_4': '444'}

        vol = update(vol, **vol_data)
        
        return {}, {}, 200

    else:
        return {}, {'vol_id': ['vol_id update forbidden'], }, 403


@app.route('/vol/<vol_id>', methods=['GET'], endpoint='vol_get')
@app_response
def vol_get(vol_id):
    """ Volume select """
    if not vol_id.isnumeric():
        return {}, {'vol_id': ['vol_id is incorrect']}, 404

    vol_id = int(vol_id)
    user_token = request.headers.get('user_token')

    this_user = user_auth(user_token)
    vol = select(Vol, id=vol_id)

    if vol:
        return {'vol': {
            'id': vol.id,
            'is_deleted': vol.is_deleted,
            'vol_title': vol.vol_title,
            'meta': {meta.meta_key: meta.meta_value for meta in vol.meta}    
        }}, {}, 200

    else:
        return {}, {'vol_id': ['vol_id not found']}, 404


@app.route('/vol/<vol_id>', methods=['DELETE'], endpoint='vol_del')
@app_response
def vol_del(vol_id):
    """ Volume delete """
    if not vol_id.isnumeric():
        return {}, {'vol_id': ['vol_id is incorrect']}, 404

    vol_id = int(vol_id)
    user_token = request.headers.get('user_token')

    this_user = user_auth(user_token)
    vol = select(Vol, id=vol_id)

    if not vol:
        return {}, {'vol_id': ['vol_id not found']}, 404

    elif this_user.can_edit:
        delete(vol)
        return {}, {}, 200

    else:
        return {}, {'vol_id': ['vol_id delete forbidden'], }, 403


@app.route('/vols/<offset>', methods=['GET'], endpoint='vol_list')
@app_response
def vol_list(offset):
    """ Volumes list """

    where = {
        'deleted': 0,
        'user_id': 2,
        'vol_title': ['VOL 4', 'VOL 3'],
    }

    extra = {
        'order_by': 'id',
        'order': 'desc',
        'offset': 0,
        'limit': 3
    }

    vols = search(Vol, where, extra)

    return {}, {}, 200
