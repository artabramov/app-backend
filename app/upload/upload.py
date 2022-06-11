from app import db
from app.core.primary_model import PrimaryModel
from marshmallow import Schema, fields, validate, ValidationError


class UploadSchema(Schema):
    user_id = fields.Int(validate=validate.Range(min=1))
    comment_id = fields.Int(validate=validate.Range(min=1))
    upload_name = db.Column(db.String(255), nullable=False, index=True)
    upload_file = db.Column(db.String(255), nullable=False, index=True)
    upload_mime = db.Column(db.String(255), nullable=False, index=True)
    upload_size = fields.Int(validate=validate.Range(min=1))


class Upload(PrimaryModel):
    __tablename__ = 'uploads'
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), index=True)
    comment_id = db.Column(db.BigInteger, db.ForeignKey('comments.id'), index=True)
    upload_name = db.Column(db.String(255), nullable=False, index=True)
    upload_file = db.Column(db.String(255), nullable=False, index=True, unique=True)
    upload_mime = db.Column(db.String(255), nullable=False, index=True)
    upload_size = db.Column(db.Integer, nullable=False)

    def __init__(self, user_id, comment_id, upload_name, upload_file, upload_mime, upload_size):
        self.user_id = user_id
        self.comment_id = comment_id
        self.upload_name = upload_name
        self.upload_file = upload_file
        self.upload_mime = upload_mime
        self.upload_size = upload_size


@db.event.listens_for(Upload, 'before_insert')
def before_insert_upload(mapper, connect, upload):
    UploadSchema().load({
        'user_id': upload.user_id,
        'comment_id': upload.comment_id,
        'upload_name': upload.upload_name,
        'upload_file': upload.upload_file,
        'upload_mime': upload.upload_mime,
        'upload_size': upload.upload_size,
    })

    if Upload.query.filter_by(upload_file=upload.upload_file).first():
        raise ValidationError({'upload_file': ['Already exists.']})


@db.event.listens_for(Upload, 'before_update')
def before_update_upload(mapper, connect, upload):
    UploadSchema().load({
        'upload_name': upload.upload_name,
    })
