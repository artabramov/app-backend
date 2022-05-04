from app import db
from app.user_meta.user_meta_schema import UserMetaSchema
from app.user_meta.user_meta_model import UserMetaModel
from marshmallow import ValidationError


def user_meta_insert_or_update(user_id, meta_key, meta_value):
    UserMetaSchema().load({
        'user_id': user_id,
        'meta_key': meta_key,
        'meta_value': meta_value,
    })

    user_meta = UserMetaModel.query.filter_by(user_id=user_id, meta_key=meta_key).first()
    if user_meta:
        user_meta.meta_value = meta_value
    else:
        user_meta = UserMetaModel(user_id, meta_key, meta_value)
    db.session.add(user_meta)
    return user_meta
