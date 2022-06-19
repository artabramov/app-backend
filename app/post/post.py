from app import db
from app.core.basic_model import BasicModel
from app.mixins.meta_mixin import MetaMixin
from marshmallow import Schema, fields, validate
from marshmallow_enum import EnumField
from app.mixins.enum_mixin import EnumMixin


class PostStatus(EnumMixin):
    draft = 0
    todo = 1
    doing = 2
    done = 3


class PostSchema(Schema):
    post_status = EnumField(PostStatus, by_value=True)
    post_title = fields.Str(validate=validate.Length(min=2, max=255))


class Post(BasicModel, MetaMixin):
    __tablename__ = 'posts'
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), index=True)
    volume_id = db.Column(db.BigInteger, db.ForeignKey('volumes.id'), index=True)
    post_status = db.Column(db.Enum(PostStatus), nullable=False, index=True)
    post_title = db.Column(db.String(255), nullable=False, index=True)
    post_sum = db.Column(db.Numeric(), nullable=False, default=0)

    meta = db.relationship('PostMeta', backref='post', lazy='subquery')
    tags = db.relationship('PostTag', backref='post', lazy='subquery')
    comments = db.relationship('Comment', backref='post', lazy='noload')

    def __init__(self, user_id, volume_id, post_status, post_title):
        self.user_id = user_id
        self.volume_id = volume_id
        self.post_status = post_status
        self.post_title = post_title
        self.post_sum = 0

    def __setattr__(self, name, value):
        if name == 'post_status':
            super().__setattr__('post_status', PostStatus.get_obj(post_status=value))
        else:
            super().__setattr__(name, value)

    def to_dict(self):
        return {
            'id': self.id,
            'created': self.created,
            'user_id': self.user_id,
            'volume_id': self.volume_id,
            'post_status': self.post_status.name,
            'post_title': self.post_title,
            'post_sum': self.post_sum,
            'tags': [tag.tag_value for tag in self.tags]
        }


@db.event.listens_for(Post, 'before_insert')
def before_insert_post(mapper, connect, post):
    PostSchema().load({
        'post_status': post.post_status,
        'post_title': post.post_title,
    })


@db.event.listens_for(Post, 'before_update')
def before_update_post(mapper, connect, post):
    PostSchema().load({
        'post_status': post.post_status,
        'post_title': post.post_title,
    })
