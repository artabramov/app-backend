from app import db
from app.core.primary_model import PrimaryModel
from app.core.meta_mixin import MetaMixin
from marshmallow import Schema, fields, validate


class VolSchema(Schema):
    user_id = fields.Int(validate=validate.Range(min=1))
    vol_title = fields.Str(validate=validate.Length(min=4, max=80))


class Vol(PrimaryModel, MetaMixin):
    __tablename__ = 'vols'
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), index=True)
    vol_title = db.Column(db.String(80), nullable=False)

    meta = db.relationship('VolMeta', backref='vols', lazy='subquery')

    def __init__(self, user_id, vol_title):
        self.user_id = user_id
        self.vol_title = vol_title


@db.event.listens_for(Vol, 'before_insert')
def before_insert_vol(mapper, connect, vol):
    VolSchema().load({
        'user_id': vol.user_id,
        'vol_title': vol.vol_title,
    })


@db.event.listens_for(Vol, 'before_update')
def before_update_vol(mapper, connect, vol):
    VolSchema().load({
        'vol_title': vol.vol_title,
    })
