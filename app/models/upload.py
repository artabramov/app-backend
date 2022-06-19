from app import db
from marshmallow import Schema, fields, validate, ValidationError
import time


class UploadSchema(Schema):
    upload_name = fields.Str(validate=validate.Length(min=1, max=255))


class Upload(db.Model):
    __tablename__ = 'uploads'
    id = db.Column(db.BigInteger, primary_key=True)
    created = db.Column(db.Integer(), nullable=False, default=lambda: int(time.time()))
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), index=True)
    comment_id = db.Column(db.BigInteger, db.ForeignKey('comments.id'), index=True)
    upload_name = db.Column(db.String(255), nullable=False, index=True)
    upload_path = db.Column(db.String(255), nullable=False, index=True, unique=True)
    upload_link = db.Column(db.String(255), nullable=False, index=True, unique=True)
    upload_mime = db.Column(db.String(255), nullable=False)
    upload_size = db.Column(db.Integer, nullable=False)

    def __init__(self, user_id, comment_id, upload_name, upload_path, upload_link, upload_mime, upload_size):
        self.user_id = user_id
        self.comment_id = comment_id
        self.upload_name = upload_name
        self.upload_path = upload_path
        self.upload_link = upload_link
        self.upload_mime = upload_mime
        self.upload_size = upload_size


@db.event.listens_for(Upload, 'before_insert')
def before_insert_upload(mapper, connect, upload):
    UploadSchema().load({
        'upload_name': upload.upload_name,
    })

    if Upload.query.filter_by(upload_path=upload.upload_path).first():
        raise ValidationError({'upload_path': ['Already exists.']})

    elif Upload.query.filter_by(upload_link=upload.upload_link).first():
        raise ValidationError({'upload_link': ['Already exists.']})


@db.event.listens_for(Upload, 'before_update')
def before_update_upload(mapper, connect, upload):
    UploadSchema().load({
        'upload_name': upload.upload_name,
    })
