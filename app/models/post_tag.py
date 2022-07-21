from app import db
from marshmallow import Schema, fields, validate, ValidationError
import time


class PostTagSchema(Schema):
    tag_value = fields.Str(validate=validate.Length(min=1, max=255))


class PostTag(db.Model):
    __tablename__ = 'posts_tags'
    __table_args__ = (db.UniqueConstraint('post_id', 'tag_value', name='posts_tag_ukey'),)
    _parent = 'post_id'
    id = db.Column(db.BigInteger, primary_key=True)
    created = db.Column(db.Integer(), nullable=False, default=lambda: int(time.time()))
    post_id = db.Column(db.BigInteger, db.ForeignKey('posts.id', ondelete='CASCADE'), index=True)
    tag_value = db.Column(db.String(255), nullable=False, index=True)

    def __init__(self, post_id, tag_value):
        self.post_id = post_id
        self.tag_value = tag_value

    @staticmethod
    def crop(value):
        post_tags = value.split(',')
        post_tags = map(lambda x: x.strip().lower(), post_tags)
        return post_tags


@db.event.listens_for(PostTag, 'before_insert')
def before_insert_post_tag(mapper, connect, post_tag):
    PostTagSchema().load({
        'tag_value': post_tag.tag_value,
    })

    if PostTag.query.filter_by(post_id=post_tag.post_id, tag_value=post_tag.tag_value).first():
        raise ValidationError({'tag_value': ['Already exists.']})


@db.event.listens_for(PostTag, 'before_update')
def before_update_post_tag(mapper, connect, post_tag):
    PostTagSchema().load({
        'tag_value': post_tag.tag_value,
    })
