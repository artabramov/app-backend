from app import db
from app.core.secondary_model import MetaModel
from marshmallow import ValidationError
from marshmallow import Schema, fields, validate


class VolMetaSchema(Schema):
    vol_id = fields.Int(validate=validate.Range(min=1))
    meta_key = fields.Str(validate=[validate.Length(min=2, max=40), lambda x: x.replace('_', '').isalnum()])
    meta_value = fields.Str(validate=validate.Length(min=1, max=255))


class VolMeta(MetaModel):
    __tablename__ = 'vols_meta'
    __table_args__ = (db.UniqueConstraint('vol_id', 'meta_key', name='vols_meta_ukey'),)
    vol_id = db.Column(db.BigInteger, db.ForeignKey('vols.id'), index=True)
    meta_key = db.Column(db.String(40), index=True, nullable=False)
    meta_value = db.Column(db.String(255), nullable=True)

    def __init__(self, vol_id, meta_key, meta_value):
        self.vol_id = vol_id
        self.meta_key = meta_key
        self.meta_value = meta_value


@db.event.listens_for(VolMeta, 'before_insert')
def before_insert_vol_meta(mapper, connect, vol_meta):
    VolMetaSchema().load({
        'vol_id': vol_meta.vol_id,
        'meta_key': vol_meta.meta_key,
        'meta_value': vol_meta.meta_value,
    })

    if VolMeta.query.filter_by(vol_id=vol_meta.vol_id, meta_key=vol_meta.meta_key).first():
        raise ValidationError({'meta_key': ['Already exists.']})


@db.event.listens_for(VolMeta, 'before_update')
def before_update_vol_meta(mapper, connect, vol_meta):
    VolMetaSchema().load({
        'vol_id': vol_meta.vol_id,
        'meta_key': vol_meta.meta_key,
        'meta_value': vol_meta.meta_value,
    })
