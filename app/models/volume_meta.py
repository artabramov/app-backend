from app import db
from marshmallow import Schema, fields, validate, ValidationError
import time


class VolumeMetaSchema(Schema):
    volume_id = fields.Int(validate=validate.Range(min=1))
    meta_key = fields.Str(validate=[validate.Length(min=2, max=40), lambda x: x.replace('_', '').isalnum()])
    meta_value = fields.Str(validate=validate.Length(min=1, max=255))


class VolumeMeta(db.Model):
    __tablename__ = 'volumes_meta'
    __table_args__ = (db.UniqueConstraint('volume_id', 'meta_key', name='volumes_meta_ukey'),)
    _parent = 'volume_id'
    id = db.Column(db.BigInteger, primary_key=True)
    created = db.Column(db.Integer(), nullable=False, default=lambda: int(time.time()))
    updated = db.Column(db.Integer(), nullable=False, default=0, onupdate=lambda: int(time.time()))
    volume_id = db.Column(db.BigInteger, db.ForeignKey('volumes.id', ondelete='CASCADE'), index=True)
    meta_key = db.Column(db.String(40), index=True, nullable=False)
    meta_value = db.Column(db.String(255), nullable=True)

    def __init__(self, volume_id, meta_key, meta_value):
        self.volume_id = volume_id
        self.meta_key = meta_key
        self.meta_value = meta_value


@db.event.listens_for(VolumeMeta, 'before_insert')
def before_insert_volume_meta(mapper, connect, volume_meta):
    VolumeMetaSchema().load({
        'volume_id': volume_meta.volume_id,
        'meta_key': volume_meta.meta_key,
        'meta_value': volume_meta.meta_value,
    })

    if VolumeMeta.query.filter_by(volume_id=volume_meta.volume_id, meta_key=volume_meta.meta_key).first():
        raise ValidationError({'meta_key': ['Already exists.']})


@db.event.listens_for(VolumeMeta, 'before_update')
def before_update_volume_meta(mapper, connect, volume_meta):
    VolumeMetaSchema().load({
        'volume_id': volume_meta.volume_id,
        'meta_key': volume_meta.meta_key,
        'meta_value': volume_meta.meta_value,
    })
