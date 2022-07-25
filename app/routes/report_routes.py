from flask import g, request
from app import app, err
from app.core.app_response import app_response
from app.core.basic_handlers import insert, update, delete, select, select_all, select_count
from app.core.user_auth import user_auth
from app.models.volume import Volume


@app.route('/report/', methods=['GET'], endpoint='report_select')
@app_response
@user_auth
def report_select():
    if not g.user.can_read:
        return {}, {'user_token': [err.PERMISSION_DENIED], }, 200

    volume_id = request.args.get('volume_id')

    volume = select(Volume, id=volume_id)
    if not volume:
        return {}, {'volume_id': [err.VALUE_NOT_FOUND]}, 200

    else:
        return {
            'volume': {
                'id': volume.id,
                'created': volume.created,
                'user_id': volume.user_id,
                'volume_currency': volume.volume_currency.name,
                'volume_title': volume.volume_title,
                'volume_summary': volume.volume_summary if volume.volume_summary else '',
                'volume_sum': volume.volume_sum,
                'meta': {meta.meta_key: meta.meta_value for meta in volume.meta if meta.meta_key in ['posts_count', 'uploads_count', 'uploads_size']}, 
            }
        }, {}, 200

