from app import db
from marshmallow import Schema, fields, validate
from marshmallow_enum import EnumField
from app.mixins.meta_mixin import MetaMixin
from app.mixins.enum_mixin import EnumMixin
import time
from app.core.app_decimal import app_decimal
from app.models.user import User
#from app.core.basic_handlers import select


class PostStatus(EnumMixin):
    draft = 0
    todo = 1
    doing = 2
    done = 3


class PostSchema(Schema):
    post_status = EnumField(PostStatus, by_value=True)
    post_title = fields.Str(validate=validate.Length(min=2, max=255))
    post_content = fields.Str(validate=validate.Length(min=2))
    post_sum = fields.Decimal()


class Post(db.Model, MetaMixin):
    __tablename__ = 'posts'
    id = db.Column(db.BigInteger, primary_key=True)
    created = db.Column(db.Integer(), nullable=False, default=lambda: int(time.time()))
    updated = db.Column(db.Integer(), nullable=False, default=0, onupdate=lambda: int(time.time()))
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), index=True)
    volume_id = db.Column(db.BigInteger, db.ForeignKey('volumes.id'), index=True)
    category_id = db.Column(db.BigInteger, db.ForeignKey('categories.id', ondelete='SET NULL'), index=True)
    post_status = db.Column(db.Enum(PostStatus), nullable=False, index=True)
    post_title = db.Column(db.String(255), nullable=False, index=True)
    post_content = db.Column(db.Text(), nullable=False)
    post_sum = db.Column(db.Numeric(), nullable=False, default=0)

    meta = db.relationship('PostMeta', backref='post', cascade='all,delete', lazy='subquery')
    tags = db.relationship('PostTag', backref='post', cascade='all,delete', lazy='subquery')
    comments = db.relationship('Comment', backref='post', cascade='all,delete', lazy='noload')
    uploads = db.relationship('Upload', backref='comment', lazy='select')

    def __init__(self, user_id, volume_id, category_id, post_status, post_title, post_content, post_sum):
        self.user_id = user_id
        self.volume_id = volume_id
        self.category_id = category_id
        self.post_status = post_status
        self.post_title = post_title
        self.post_content = post_content
        self.post_sum = post_sum

    def __setattr__(self, name, value):
        if name == 'post_status':
            super().__setattr__('post_status', PostStatus.get_enum(post_status=value))
        else:
            super().__setattr__(name, value)

    def to_dict(self):
        return {
            'id': self.id,
            'created': self.created,
            'user_id': self.user_id,
            'volume_id': self.volume_id,
            'category_id': self.category_id,
            'post_status': self.post_status.name,
            'post_title': self.post_title,
            'post_content': self.post_content,
            'post_sum': self.post_sum,
            'tags': [tag.tag_value for tag in self.tags],
            'meta': {
                meta.meta_key: meta.meta_value for meta in self.meta if meta.meta_key in ['uploads_count', 'uploads_size', 'comments_count']
            },
            'user': self.user.to_dict(),
            'volume': self.volume.to_dict(),
            'category': self.category.to_dict(),
        }


@db.event.listens_for(Post, 'before_insert')
def before_insert_post(mapper, connect, post):
    PostSchema().load({
        'post_status': post.post_status,
        'post_title': post.post_title,
        'post_content': post.post_content,
        'post_sum': post.post_sum,
    })
    post.post_sum = app_decimal(post.post_sum)


@db.event.listens_for(Post, 'before_update')
def before_update_post(mapper, connect, post):
    PostSchema().load({
        'post_status': post.post_status,
        'post_title': post.post_title,
        'post_content': post.post_content,
        'post_sum': post.post_sum,
    })
    post.post_sum = app_decimal(post.post_sum)
