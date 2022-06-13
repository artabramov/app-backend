from flask import g, request
from app import app
from app.core.app_response import app_response
from app.core.basic_handlers import insert, update, delete, select, select_all
from app.volume.volume import Volume
from app.core.user_auth import user_auth


@app.route('/volume/', methods=['POST'], endpoint='volume_post')
@app_response
@user_auth
def volume_post():
    """ Volume insert """
    if not g.user.can_edit:
        return {}, {'user_token': ['user_token have not permissions for volume edit'], }, 406

    volume_title = request.args.get('volume_title')
    volume_currency = request.args.get('volume_currency')

    volume_meta = {
        'key_1': 'value 1!!!',
        'key_2': 'value 2!!!',
        'key_3': 'value 3!!!',
    }

    volume = insert(Volume, user_id=g.user.id, volume_title=volume_title, volume_currency=volume_currency, meta=volume_meta)
    return {
        'volume': str(volume)
    }, {}, 201


@app.route('/volume/<int:volume_id>', methods=['PUT'], endpoint='volume_put')
@app_response
@user_auth
def volume_put(volume_id):
    """ Volume update """
    if not g.user.can_edit:
        return {}, {'user_token': ['user_token must have edit permissions'], }, 406

    volume_title = request.args.get('volume_title')
    volume_currency = request.args.get('volume_currency')

    volume = select(Volume, id=volume_id)
    if not volume:
        return {}, {'volume_id': ['volume_id not found']}, 404

    volume_data = {}
    if volume_title:
        volume_data['volume_title'] = volume_title
    if volume_currency:
        volume_data['volume_currency'] = volume_currency

    volume_data['meta'] = {
        'key_1': '444444444444444444444444444444444', 
        'key_2': '222-222-333',
        'key_3': None,
        'key_4': '444'}

    volume = update(volume, **volume_data)
    return {}, {}, 200


@app.route('/volume/<int:volume_id>', methods=['GET'], endpoint='volume_get')
@app_response
@user_auth
def volume_get(volume_id):
    """ Volume select """
    if g.user.can_read:
        return {}, {'user_token': ['user_token must have read permissions'], }, 406

    volume = select(Volume, id=volume_id)
    if volume:
        return {'volume': {
            'id': volume.id,
            'is_deleted': volume.is_deleted,
            'volume_title': volume.volume_title,
            'meta': {meta.meta_key: meta.meta_value for meta in volume.meta}    
        }}, {}, 200

    else:
        return {}, {'volume_id': ['volume_id not found']}, 404


@app.route('/volume/<int:volume_id>', methods=['DELETE'], endpoint='volume_del')
@app_response
@user_auth
def volume_del(volume_id):
    """ Volume delete """
    if not g.user.can_edit:
        return {}, {'user_token': ['user_token must have edit permissions'], }, 406

    volume = select(Volume, id=volume_id)
    if not volume:
        return {}, {'volume_id': ['volume_id not found']}, 404

    delete(volume)
    return {}, {}, 200


@app.route('/volumes/<int:offset>', methods=['GET'], endpoint='volumes_list')
@app_response
@user_auth
def volumes_list(offset):
    """ Volumes list """
    if not g.user.can_read:
        return {}, {'user_token': ['user_token must have read permissions'], }, 406

    volumes = select_all(Volume, deleted=0)
    return {}, {}, 200
