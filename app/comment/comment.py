from app import db
from app.core.basic_model import BasicModel
from marshmallow import Schema, fields, validate, ValidationError
from decimal import Decimal
from app.core.app_decimal import app_decimal


class CommentSchema(Schema):
    user_id = fields.Int(validate=validate.Range(min=1))
    post_id = fields.Int(validate=validate.Range(min=1))
    comment_content = fields.Str(validate=validate.Length(min=2))
    comment_sum = fields.Decimal()


class Comment(BasicModel):
    __tablename__ = 'comments'
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), index=True)
    post_id = db.Column(db.BigInteger, db.ForeignKey('posts.id'), index=True)
    comment_content = db.Column(db.Text(), nullable=False)
    comment_sum = db.Column(db.Numeric(), nullable=False, default=0)

    uploads = db.relationship('Upload', backref='comment', lazy='subquery')

    def __init__(self, user_id, post_id, comment_content, comment_sum=0):
        self.user_id = user_id
        self.post_id = post_id
        self.comment_content = comment_content
        self.comment_sum = comment_sum

@db.event.listens_for(Comment, 'before_insert')
def before_insert_comment(mapper, connect, comment):
    CommentSchema().load({
        'user_id': comment.user_id,
        'post_id': comment.post_id,
        'comment_content': comment.comment_content,
        'comment_sum': comment.comment_sum,
    })
    comment.comment_sum = app_decimal(comment.comment_sum)


@db.event.listens_for(Comment, 'before_update')
def before_update_comment(mapper, connect, comment):
    CommentSchema().load({
        'comment_content': comment.comment_content,
        'comment_sum': comment.comment_sum,
    })
    comment.comment_sum = app_decimal(comment.comment_sum)