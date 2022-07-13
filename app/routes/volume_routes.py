from flask import g, request
from app import app, err
from app.core.app_response import app_response
from app.core.basic_handlers import insert, update, delete, select, select_all, select_count
from app.models.volume import Volume #, VolumeCurrency
from app.core.user_auth import user_auth
from app.models.user import User

VOLUME_SELECT_LIMIT = app.config['VOLUME_SELECT_LIMIT']

def to_dict(volume):
    user = select(User, id=volume.user_id)
    return {
        'id': volume.id,
        'created': volume.created,
        'user_id': volume.user_id,
        'user': {'user_login': user.user_login},
        'volume_currency': volume.volume_currency.name,
        'volume_title': volume.volume_title,
        'volume_summary': volume.volume_summary if volume.volume_summary else '',
        'volume_sum': volume.volume_sum,
        'meta': {meta.meta_key: meta.meta_value for meta in volume.meta if meta.meta_key in ['posts_count', 'uploads_count', 'uploads_size']}, 
    }


@app.route('/volume/', methods=['POST'], endpoint='volume_insert')
@app_response
@user_auth
def volume_insert():
    if not g.user.can_admin:
        return {}, {'user_token': [err.PERMISSION_DENIED], }, 200

    volume_title = request.args.get('volume_title')
    volume_currency = request.args.get('volume_currency')
    volume_summary = request.args.get('volume_summary', '')

    volume = insert(Volume, user_id=g.user.id, volume_title=volume_title, volume_summary=volume_summary, volume_currency=volume_currency, meta={})
    return {'volume_id': volume.id}, {}, 201


@app.route('/volume/<int:volume_id>/', methods=['PUT'], endpoint='volume_update')
@app_response
@user_auth
def volume_update(volume_id):
    if not g.user.can_admin:
        return {}, {'user_token': [err.PERMISSION_DENIED], }, 200

    volume_title = request.args.get('volume_title', '')
    volume_currency = request.args.get('volume_currency', '')
    volume_summary = request.args.get('volume_summary', '')

    volume = select(Volume, id=volume_id)
    if not volume:
        return {}, {'volume_id': [err.VALUE_NOT_FOUND]}, 200

    volume_data = {}
    if volume_title:
        volume_data['volume_title'] = volume_title

    if volume_currency:
        volume_data['volume_currency'] = volume_currency

    if volume_summary:
        volume_data['volume_summary'] = volume_summary

    volume = update(volume, **volume_data, meta={})
    return {}, {}, 200


@app.route('/volume/<int:volume_id>/', methods=['GET'], endpoint='volume_select')
@app_response
@user_auth
def volume_select(volume_id):
    if not g.user.can_read:
        return {}, {'user_token': [err.PERMISSION_DENIED], }, 200

    volume = select(Volume, id=volume_id)
    if volume:
        return {'volume': to_dict(volume)}, {}, 200

    else:
        return {}, {'volume_id': [err.VALUE_NOT_FOUND]}, 200


@app.route('/volume/<int:volume_id>/', methods=['DELETE'], endpoint='volume_delete')
@app_response
@user_auth
def volume_delete(volume_id):
    if not g.user.can_admin:
        return {}, {'user_token': [err.PERMISSION_DENIED], }, 200

    volume = select(Volume, id=volume_id)
    if not volume:
        return {}, {'volume_id': [err.VALUE_NOT_FOUND]}, 200

    delete(volume)
    return {}, {}, 200


@app.route('/volumes/', methods=['GET'], endpoint='volumes_list')
@app_response
@user_auth
def volumes_list():
    if not g.user.can_read:
        return {}, {'user_token': [err.PERMISSION_DENIED], }, 200

    volumes = select_all(Volume)
    return {
        'volumes': [to_dict(volume) for volume in volumes],
    }, {}, 200
