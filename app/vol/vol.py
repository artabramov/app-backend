from app import db
from app.core.basic_model import BasicModel
from app.core.meta_mixin import MetaMixin
from marshmallow import Schema, fields, validate
from marshmallow_enum import EnumField
from enum import Enum


class VolCurrency(Enum):
    USD = 840
    EUR = 978
    GBP = 826
    CHF = 756

    @classmethod
    def get_value(cls, value):
        return cls._member_map_[value] if value in cls._member_map_ else value


class VolSchema(Schema):
    user_id = fields.Int(validate=validate.Range(min=1))
    vol_title = fields.Str(validate=validate.Length(min=4, max=80))
    vol_currency = EnumField(VolCurrency, by_value=True)
    vol_sum = fields.Decimal()
    posts_count = fields.Int(validate=validate.Range(min=0))


class Vol(BasicModel, MetaMixin):
    __tablename__ = 'vols'
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), index=True)
    vol_title = db.Column(db.String(80), nullable=False)
    vol_currency = db.Column(db.Enum(VolCurrency), nullable=False, default='USD')
    vol_sum = db.Column(db.Numeric(), nullable=False, default=0)
    #vol_sum = db.Column(db.Numeric(precision=8, scale=4), nullable=False, default=0)
    posts_count = db.Column(db.BigInteger, nullable=False, default=0)

    meta = db.relationship('VolMeta', backref='vols', lazy='subquery')

    def __init__(self, user_id, vol_title, vol_currency):
        self.user_id = user_id
        self.vol_title = vol_title
        self.vol_currency = vol_currency
        self.vol_sum = 0
        self.posts_count = 0


@db.event.listens_for(Vol, 'before_insert')
def before_insert_vol(mapper, connect, vol):
    VolSchema().load({
        'user_id': vol.user_id,
        'vol_title': vol.vol_title,
        'vol_currency': VolCurrency.get_value(vol.vol_currency),
    })


@db.event.listens_for(Vol, 'before_update')
def before_update_vol(mapper, connect, vol):
    VolSchema().load({
        'vol_title': vol.vol_title,
        'vol_currency': VolCurrency.get_value(vol.vol_currency),
    })
