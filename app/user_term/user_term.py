from app import db
from app.core.base_model import BaseModel
from marshmallow import ValidationError
from marshmallow import Schema, fields, validate

USER_TERM_KEYS = {'key_1', 'key_2', 'key_3', 'key_4'}


class UserTermSchema(Schema):
    user_id = fields.Int(validate=validate.Range(min=1))
    term_key = fields.Str(validate=lambda x: x in USER_TERM_KEYS)
    term_value = fields.Str(validate=validate.Length(min=1, max=255))


class UserTerm(BaseModel):
    __tablename__ = 'users_terms'
    __table_args__ = (db.UniqueConstraint('user_id', 'term_key', name='users_terms_ukey'),)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), index=True)
    term_key = db.Column(db.String(40), index=True, nullable=False)
    term_value = db.Column(db.String(255), nullable=True)

    def __init__(self, user_id, term_key, term_value):
        #user_term = UserTerm.query.filter_by(user_id=user_id, term_key=term_key).first()
        #if user_term:
        #    for k in [k for k in user_term.__dict__ if not k.startswith('_')]:
        #        setattr(self, k, user_term.__dict__[k])
        #    pass
        #else:
        
        self.user_id = user_id
        self.term_key = term_key
        self.term_value = term_value

    @classmethod
    def set_term(cls, user_id, term_key, term_value):
        user_term = cls.query.filter_by(user_id=user_id, term_key=term_key).first()
        if user_term:
            user_term.term_value = term_value
        else:
            user_term = cls(user_id, term_key, term_value)
        return user_term


@db.event.listens_for(UserTerm, 'before_insert')
def before_insert_user_term(mapper, connect, user_term):
    UserTermSchema().load({
        'user_id': user_term.user_id,
        'term_key': user_term.term_key,
        'term_value': user_term.term_value,
    })

    if UserTerm.query.filter_by(user_id=user_term.user_id, term_key=user_term.term_key).first():
        raise ValidationError({'term_key': ['Already exists.']})


@db.event.listens_for(UserTerm, 'before_update')
def before_update_user(mapper, connect, user_term):
    UserTermSchema().load({
        'user_id': user_term.user_id,
        'term_key': user_term.term_key,
        'term_value': user_term.term_value,
    })
