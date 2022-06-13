from app import db
from app.core.tag_model import TagModel
from marshmallow import ValidationError
from marshmallow import Schema, fields, validate


class PostTagSchema(Schema):
    post_id = fields.Int(validate=validate.Range(min=1))
    tag_value = fields.Str(validate=validate.Length(min=1, max=255))


class PostTag(TagModel):
    __tablename__ = 'posts_tags'
    __table_args__ = (db.UniqueConstraint('post_id', 'tag_value', name='posts_tag_ukey'),)
    post_id = db.Column(db.BigInteger, db.ForeignKey('posts.id'), index=True)
    tag_value = db.Column(db.String(255), nullable=True, index=True)

    def __init__(self, post_id, tag_value):
        self.post_id = post_id
        self.tag_value = tag_value


@db.event.listens_for(PostTag, 'before_insert')
def before_insert_post_tag(mapper, connect, post_tag):
    PostTagSchema().load({
        'post_id': post_tag.post_id,
        'tag_value': post_tag.tag_value,
    })

    if PostTag.query.filter_by(post_id=post_tag.post_id, tag_value=post_tag.tag_value).first():
        raise ValidationError({'tag_value': ['Already exists.']})


@db.event.listens_for(PostTag, 'before_update')
def before_update_post_tag(mapper, connect, post_tag):
    PostTagSchema().load({
        'post_id': post_tag.post_id,
        'tag_value': post_tag.tag_value,
    })
