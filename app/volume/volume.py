from app import db
from app.core.basic_model import BasicModel
from app.core.meta_mixin import MetaMixin
from marshmallow import Schema, fields, validate
from marshmallow_enum import EnumField
from app.core.enum_mixin import EnumMixin

class VolumeCurrency(EnumMixin):
    USD = 840
    EUR = 978
    GBP = 826
    CHF = 756


class VolumeSchema(Schema):
    volume_title = fields.Str(validate=validate.Length(min=4, max=80))
    volume_currency = EnumField(VolumeCurrency, by_value=True)


class Volume(BasicModel, MetaMixin):
    __tablename__ = 'volumes'
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), index=True)
    volume_title = db.Column(db.String(80), nullable=False)
    volume_currency = db.Column(db.Enum(VolumeCurrency), nullable=False)
    volume_sum = db.Column(db.Numeric(), nullable=False, default=0)

    meta = db.relationship('VolumeMeta', backref='volume', lazy='subquery')
    posts = db.relationship('Post', backref='volume', lazy='noload')

    def __init__(self, user_id, volume_title, volume_currency):
        self.user_id = user_id
        self.volume_title = volume_title
        self.volume_currency = volume_currency

    def __setattr__(self, name, value):
        if name == 'volume_currency':
            super().__setattr__('volume_currency', VolumeCurrency.get_obj(volume_currency=value))
        else:
            super().__setattr__(name, value)

    def to_dict(self):
        return {
            'id': self.id,
            'created': self.created,
            'volume_currency': self.volume_currency.name,
            'volume_title': self.volume_title,
            'volume_sum': self.volume_sum,
        }


@db.event.listens_for(Volume, 'before_insert')
def before_insert_volume(mapper, connect, volume):
    VolumeSchema().load({
        'volume_title': volume.volume_title,
        'volume_currency': volume.volume_currency,
    })


@db.event.listens_for(Volume, 'before_update')
def before_update_volume(mapper, connect, volume):
    VolumeSchema().load({
        'volume_title': volume.volume_title,
        'volume_currency': volume.volume_currency,
    })
