from app import db
from app.core.primary_model import PrimaryModel
from app.core.meta_mixin import MetaMixin
from marshmallow import Schema, fields, validate


class PostSchema(Schema):
    user_id = fields.Int(validate=validate.Range(min=1))
    vol_id = fields.Int(validate=validate.Range(min=1))
    post_title = fields.Str(validate=validate.Length(min=4, max=255))
    comments_sum = fields.Decimal()
    comments_count = fields.Int(validate=validate.Range(min=0))
    uploads_size = fields.Int(validate=validate.Range(min=0))
    uploads_count = fields.Int(validate=validate.Range(min=0))


class Post(PrimaryModel, MetaMixin):
    __tablename__ = 'posts'
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), index=True)
    vol_id = db.Column(db.BigInteger, db.ForeignKey('vols.id'), index=True)
    post_title = db.Column(db.String(255), nullable=False, index=True)
    comments_sum = db.Column(db.Numeric(), nullable=False, default=0)
    comments_count = db.Column(db.BigInteger, nullable=False, default=0)
    uploads_size = db.Column(db.BigInteger, nullable=False, default=0)
    uploads_count = db.Column(db.BigInteger, nullable=False, default=0)

    meta = db.relationship('PostMeta', backref='posts', lazy='subquery')
    tags = db.relationship('PostTag', backref='tags', lazy='subquery')

    def __init__(self, user_id, vol_id, post_title):
        self.user_id = user_id
        self.vol_id = vol_id
        self.post_title = post_title
        self.comments_sum = 0
        self.comments_count = 0
        self.uploads_size = 0
        self.uploads_count = 0


@db.event.listens_for(Post, 'before_insert')
def before_insert_post(mapper, connect, post):
    PostSchema().load({
        'user_id': post.user_id,
        'vol_id': post.vol_id,
        'post_title': post.post_title,
    })


@db.event.listens_for(Post, 'before_update')
def before_update_post(mapper, connect, post):
    PostSchema().load({
        'post_title': post.post_title,
    })
