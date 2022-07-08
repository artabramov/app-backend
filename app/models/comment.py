from app import db
from marshmallow import Schema, fields, validate
import time


class CommentSchema(Schema):
    user_id = fields.Int(validate=validate.Range(min=1))
    post_id = fields.Int(validate=validate.Range(min=1))
    comment_content = fields.Str(validate=validate.Length(min=2))


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.BigInteger, primary_key=True)
    created = db.Column(db.Integer(), nullable=False, default=lambda: int(time.time()))
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), index=True)
    post_id = db.Column(db.BigInteger, db.ForeignKey('posts.id'), index=True)
    comment_content = db.Column(db.Text(), nullable=False)

    def __init__(self, user_id, post_id, comment_content):
        self.user_id = user_id
        self.post_id = post_id
        self.comment_content = comment_content

    def to_dict(self):
        return {
            'id': self.id, 
            'created': self.created, 
            'comment_content': self.comment_content,
            'user': self.user.to_dict(),
        }


@db.event.listens_for(Comment, 'before_insert')
def before_insert_comment(mapper, connect, comment):
    CommentSchema().load({
        'user_id': comment.user_id,
        'post_id': comment.post_id,
        'comment_content': comment.comment_content,
    })


@db.event.listens_for(Comment, 'before_update')
def before_update_comment(mapper, connect, comment):
    CommentSchema().load({
        'comment_content': comment.comment_content,
    })
