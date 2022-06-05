from flask import request
from app import app
from app.core.app_response import app_response
from app.user.user_handlers import user_auth
from app.vol.vol_handlers import vol_insert, vol_update, vol_select, vol_delete, vol_search


@app.route('/vol/', methods=['POST'], endpoint='vol_post')
@app_response
def vol_post():
    """ Volume insert """
    user_token = request.headers.get('user_token')
    vol_title = request.args.get('vol_title', None)

    this_user = user_auth(user_token)

    if not this_user.can_edit:
        return {}, {'user_token': ['user_token have not permissions for vol edit'], }, 406

    vol_meta = {
        'key_1': 'value 1!!!',
        'key_2': 'value 2!!!',
        'key_3': 'value 3!!!',
    }

    #vol = vol_insert(this_user.id, vol_title, vol_meta)
    from app.core.primary_handlers import insert
    from app.vol.vol import Vol
    from app.vol.vol_meta import VolMeta
    vol = insert(Vol, user_id=this_user.id, vol_title=vol_title, meta=vol_meta)

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

    this_user = user_auth(user_token)

    from app.core.primary_handlers import select
    from app.vol.vol import Vol
    vol = select(Vol, id=vol_id)

    if not vol:
        return {}, {'vol_id': ['vol_id not found']}, 404

    elif this_user.can_edit:
        vol_data = {}
        if vol_title:
            vol_data['vol_title'] = vol_title

        vol_data['meta'] = {
            'key_1': 'value 222!', 
            'key_2': 'None2!',
            'key_3': None,
            'key_4': '2'}

        #vol_update(vol, **vol_data)
        
        from app.core.primary_handlers import update
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
    #vol = vol_select(id=vol_id)

    from app.core.primary_handlers import select
    from app.vol.vol import Vol
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
    vol = vol_select(id=vol_id)

    if not vol:
        return {}, {'vol_id': ['vol_id not found']}, 404

    elif this_user.can_edit:
        from app.core.primary_handlers import delete
        delete(vol)
        return {}, {}, 200

    else:
        return {}, {'vol_id': ['vol_id delete forbidden'], }, 403


@app.route('/vols/<offset>', methods=['GET'], endpoint='vol_list')
@app_response
def vol_list(offset):
    """ Volumes list """

    where = {
        'user_id': 2,
        'vol_title': ['VOL 4', 'VOL 3'],
    }

    extra = {
        'order_by': 'id',
        'order': 'desc',
        'offset': 0,
        'limit': 5
    }

    vols = vol_search(where)

    return {}, {}, 200


