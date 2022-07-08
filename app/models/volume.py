from app import db
from marshmallow import Schema, fields, validate
from marshmallow_enum import EnumField
from app.mixins.meta_mixin import MetaMixin
from app.mixins.enum_mixin import EnumMixin
import time


class VolumeCurrency(EnumMixin):
    USD = 840
    EUR = 978
    GBP = 826
    CHF = 756


class VolumeSchema(Schema):
    volume_title = fields.Str(validate=validate.Length(min=2, max=128))
    volume_summary = fields.Str(validate=validate.Length(max=255))
    volume_currency = EnumField(VolumeCurrency, by_value=True)


class Volume(db.Model, MetaMixin):
    __tablename__ = 'volumes'
    id = db.Column(db.BigInteger, primary_key=True)
    created = db.Column(db.Integer(), nullable=False, default=lambda: int(time.time()))
    updated = db.Column(db.Integer(), nullable=False, default=0, onupdate=lambda: int(time.time()))
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), index=True)
    volume_title = db.Column(db.String(128), nullable=False)
    volume_summary = db.Column(db.String(255), nullable=True)
    volume_currency = db.Column(db.Enum(VolumeCurrency), nullable=False)
    volume_sum = db.Column(db.Numeric(), nullable=False, default=0)

    meta = db.relationship('VolumeMeta', backref='volume', cascade='all,delete', lazy='subquery')
    posts = db.relationship('Post', backref='volume', cascade='all,delete', lazy='noload')

    def __init__(self, user_id, volume_title, volume_currency, volume_summary=None):
        self.user_id = user_id
        self.volume_title = volume_title
        self.volume_currency = volume_currency
        self.volume_summary = volume_summary

    def __setattr__(self, name, value):
        if name == 'volume_currency':
            super().__setattr__('volume_currency', VolumeCurrency.get_enum(volume_currency=value))
        else:
            super().__setattr__(name, value)

    def to_dict(self):
        return {
            'id': self.id,
            'created': self.created,
            'volume_currency': self.volume_currency.name,
            'volume_title': self.volume_title,
            'volume_summary': self.volume_summary if self.volume_summary else '',
            'volume_sum': self.volume_sum,
            'meta': {
                meta.meta_key: meta.meta_value for meta in self.meta if meta.meta_key in ['posts_count', 'uploads_count', 'uploads_size']
            } 
        }


@db.event.listens_for(Volume, 'before_insert')
def before_insert_volume(mapper, connect, volume):
    volume_data = {
        'volume_title': volume.volume_title,
        'volume_currency': volume.volume_currency,
    }

    if volume.volume_summary:
        volume_data['volume_summary'] = volume.volume_summary

    VolumeSchema().load(volume_data)


@db.event.listens_for(Volume, 'before_update')
def before_update_volume(mapper, connect, volume):
    volume_data = {
        'volume_title': volume.volume_title,
        'volume_currency': volume.volume_currency,
    }

    if volume.volume_summary:
        volume_data['volume_summary'] = volume.volume_summary

    VolumeSchema().load(volume_data)
