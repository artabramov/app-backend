from flask import g, request
from app import app, err
from app.core.app_response import app_response
from app.core.basic_handlers import insert, update, delete, select, select_all, select_count
from app.models.volume import Volume #, VolumeCurrency
from app.core.user_auth import user_auth

VOLUME_SELECT_LIMIT = app.config['VOLUME_SELECT_LIMIT']


@app.route('/volume/', methods=['POST'], endpoint='volume_insert')
@app_response
@user_auth
def volume_insert():
    if not g.user.can_admin:
        return {}, {'user_token': [err.NOT_ALLOWED], }, 400

    volume_title = request.args.get('volume_title')
    volume_currency = request.args.get('volume_currency')

    volume = insert(Volume, user_id=g.user.id, volume_title=volume_title, volume_currency=volume_currency)
    return {'volume_id': volume.id}, {}, 200


@app.route('/volume/<int:volume_id>', methods=['PUT'], endpoint='volume_update')
@app_response
@user_auth
def volume_update(volume_id):
    if not g.user.can_admin:
        return {}, {'user_token': [err.NOT_ALLOWED], }, 400

    volume_title = request.args.get('volume_title', '')
    volume_currency = request.args.get('volume_currency', '')

    volume = select(Volume, id=volume_id)
    if not volume:
        return {}, {'volume_id': [err.NOT_FOUND]}, 404

    volume_data = {}
    if volume_title:
        volume_data['volume_title'] = volume_title

    if volume_currency:
        volume_data['volume_currency'] = volume_currency

    volume = update(volume, **volume_data)
    return {}, {}, 200


@app.route('/volume/<int:volume_id>', methods=['GET'], endpoint='volume_select')
@app_response
@user_auth
def volume_select(volume_id):
    if not g.user.can_read:
        return {}, {'user_token': [err.NOT_ALLOWED], }, 400

    volume = select(Volume, id=volume_id)
    if volume:
        return {'volume': volume.to_dict()}, {}, 200

    else:
        return {}, {'volume_id': [err.NOT_FOUND]}, 404


@app.route('/volume/<int:volume_id>', methods=['DELETE'], endpoint='volume_delete')
@app_response
@user_auth
def volume_delete(volume_id):
    if not g.user.can_admin:
        return {}, {'user_token': [err.NOT_ALLOWED], }, 400

    volume = select(Volume, id=volume_id)
    if not volume:
        return {}, {'volume_id': [err.NOT_FOUND]}, 404

    delete(volume)
    return {}, {}, 200


@app.route('/volumes/<int:offset>', methods=['GET'], endpoint='volumes_list')
@app_response
@user_auth
def volumes_list(offset):
    if not g.user.can_read:
        return {}, {'user_token': [err.NOT_ALLOWED], }, 400

    volumes = select_all(Volume, offset=offset, limit=VOLUME_SELECT_LIMIT)
    volumes_count = select_count(Volume)

    return {
        'volumes': [volume.to_dict() for volume in volumes],
        'volumes_count': volumes_count,
    }, {}, 200
