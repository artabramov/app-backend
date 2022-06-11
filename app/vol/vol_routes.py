from flask import g, request
from app import app
from app.core.app_response import app_response
from app.core.basic_handlers import insert, update, delete, select, search
from app.vol.vol import Vol
from app.core.user_auth import user_auth


@app.route('/vol/', methods=['POST'], endpoint='vol_post')
@app_response
@user_auth
def vol_post():
    """ Volume insert """
    if not g.user.can_edit:
        return {}, {'user_token': ['user_token have not permissions for vol edit'], }, 406

    vol_title = request.args.get('vol_title')
    vol_currency = request.args.get('vol_currency')

    vol_meta = {
        'key_1': 'value 1!!!',
        'key_2': 'value 2!!!',
        'key_3': 'value 3!!!',
    }

    vol = insert(Vol, user_id=g.user.id, vol_title=vol_title, vol_currency=vol_currency, meta=vol_meta)
    return {
        'vol': str(vol)
    }, {}, 201


@app.route('/vol/<int:vol_id>', methods=['PUT'], endpoint='vol_put')
@app_response
@user_auth
def vol_put(vol_id):
    """ Volume update """
    if g.user.can_edit:
        return {}, {'user_token': ['user_token must have edit permissions'], }, 406

    vol_title = request.args.get('vol_title')
    vol_currency = request.args.get('vol_currency')

    vol = select(Vol, id=vol_id)
    if not vol:
        return {}, {'vol_id': ['vol_id not found']}, 404

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


@app.route('/vol/<int:vol_id>', methods=['GET'], endpoint='vol_get')
@app_response
@user_auth
def vol_get(vol_id):
    """ Volume select """
    if g.user.can_read:
        return {}, {'user_token': ['user_token must have read permissions'], }, 406

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


@app.route('/vol/<int:vol_id>', methods=['DELETE'], endpoint='vol_del')
@app_response
@user_auth
def vol_del(vol_id):
    """ Volume delete """
    if g.user.can_edit:
        return {}, {'user_token': ['user_token must have edit permissions'], }, 406

    vol = select(Vol, id=vol_id)
    if not vol:
        return {}, {'vol_id': ['vol_id not found']}, 404

    delete(vol)
    return {}, {}, 200


@app.route('/vols/<int:offset>', methods=['GET'], endpoint='vol_list')
@app_response
@user_auth
def vol_list(offset):
    """ Volumes list """
    if g.user.can_read:
        return {}, {'user_token': ['user_token must have read permissions'], }, 406

    where = {
        'deleted': 0,
        'user_id': 2,
        'vol_title': ['VOL 4', 'VOL 3'],
    }

    results_on_page = 2

    extra = {
        'order_by': 'id',
        'order': 'desc',
        'offset': offset * results_on_page,
        'limit': 3
    }

    vols = search(Vol, where, extra)
    return {}, {}, 200
