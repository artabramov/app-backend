from app import db
from marshmallow import Schema, fields, validate
import time


class CategorySchema(Schema):
    category_title = fields.Str(validate=validate.Length(min=2, max=128))
    category_summary = fields.Str(validate=validate.Length(max=255))


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.BigInteger, primary_key=True)
    created = db.Column(db.Integer(), nullable=False, default=lambda: int(time.time()))
    updated = db.Column(db.Integer(), nullable=False, default=0, onupdate=lambda: int(time.time()))
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), index=True)
    category_title = db.Column(db.String(128), nullable=False)
    category_summary = db.Column(db.String(255), nullable=True)

    posts = db.relationship('Post', backref='category', lazy='noload')

    def __init__(self, user_id, category_title, category_summary):
        self.user_id = user_id
        self.category_title = category_title
        self.category_summary = category_summary

    def to_dict(self):
        return {
            'id': self.id,
            'created': self.created,
            'user_id': self.user_id,
            'category_title': self.category_title,
            'category_summary': self.category_summary,
        }


@db.event.listens_for(Category, 'before_insert')
def before_insert_category(mapper, connect, category):
    category_data = {
        'category_title': category.category_title,
    }

    if category.category_summary:
        category_data['category_summary'] = category.category_summary

    CategorySchema().load(category_data)


@db.event.listens_for(Category, 'before_update')
def before_update_category(mapper, connect, category):
    category_data = {
        'category_title': category.category_title,
    }

    if category.category_summary:
        category_data['category_summary'] = category.category_summary

    CategorySchema().load(category_data)
