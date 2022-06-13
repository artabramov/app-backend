from app import db
from app.core.basic_model import BasicModel
from app.core.meta_mixin import MetaMixin
from marshmallow import Schema, fields, validate
from marshmallow_enum import EnumField
from enum import Enum


class PostStatus(Enum):
    draft = 0
    todo = 1
    doing = 2
    done = 3

    @classmethod
    def get_value(cls, value):
        return cls._member_map_[value] if value in cls._member_map_ else value


class PostSchema(Schema):
    user_id = fields.Int(validate=validate.Range(min=1))
    vol_id = fields.Int(validate=validate.Range(min=1))
    post_status = EnumField(PostStatus, by_value=True)
    post_title = fields.Str(validate=validate.Length(min=4, max=255))
    post_sum = fields.Decimal()


class Post(BasicModel, MetaMixin):
    __tablename__ = 'posts'
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), index=True)
    vol_id = db.Column(db.BigInteger, db.ForeignKey('vols.id'), index=True)
    post_status = db.Column(db.Enum(PostStatus), nullable=False, index=True)
    post_title = db.Column(db.String(255), nullable=False, index=True)
    post_sum = db.Column(db.Numeric(), nullable=False, default=0)

    meta = db.relationship('PostMeta', backref='post', lazy='subquery')
    tags = db.relationship('PostTag', backref='post', lazy='subquery')
    comments = db.relationship('Comment', backref='post', lazy='noload')

    def __init__(self, user_id, vol_id, post_status, post_title):
        self.user_id = user_id
        self.vol_id = vol_id
        self.post_status = post_status
        self.post_title = post_title
        self.post_sum = 0


@db.event.listens_for(Post, 'before_insert')
def before_insert_post(mapper, connect, post):
    PostSchema().load({
        'user_id': post.user_id,
        'vol_id': post.vol_id,
        'post_status': PostStatus.get_value(post.post_status),
        'post_title': post.post_title,
    })


@db.event.listens_for(Post, 'before_update')
def before_update_post(mapper, connect, post):
    PostSchema().load({
        'post_status': PostStatus.get_value(post.post_status),
        'post_title': post.post_title,
    })
