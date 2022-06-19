from app import db
from app.core.meta_model import MetaModel
from marshmallow import ValidationError
from marshmallow import Schema, fields, validate


class PostMetaSchema(Schema):
    meta_key = fields.Str(validate=[validate.Length(min=2, max=40), lambda x: x.replace('_', '').isalnum()])
    meta_value = fields.Str(validate=validate.Length(min=1, max=255))


class PostMeta(MetaModel):
    __tablename__ = 'posts_meta'
    __table_args__ = (db.UniqueConstraint('post_id', 'meta_key', name='posts_meta_ukey'),)
    post_id = db.Column(db.BigInteger, db.ForeignKey('posts.id'), index=True)
    meta_key = db.Column(db.String(40), index=True, nullable=False)
    meta_value = db.Column(db.String(255), nullable=True)

    def __init__(self, post_id, meta_key, meta_value):
        self.post_id = post_id
        self.meta_key = meta_key
        self.meta_value = meta_value


@db.event.listens_for(PostMeta, 'before_insert')
def before_insert_post_meta(mapper, connect, post_meta):
    PostMetaSchema().load({
        'meta_key': post_meta.meta_key,
        'meta_value': post_meta.meta_value,
    })

    if PostMeta.query.filter_by(post_id=post_meta.post_id, meta_key=post_meta.meta_key).first():
        raise ValidationError({'meta_key': ['Already exists.']})


@db.event.listens_for(PostMeta, 'before_update')
def before_update_post_meta(mapper, connect, post_meta):
    PostMetaSchema().load({
        'meta_key': post_meta.meta_key,
        'meta_value': post_meta.meta_value,
    })
