from app import db
from app.core.base_model import BaseModel
from marshmallow import ValidationError
from marshmallow import Schema, fields, validate

USER_TERM_KEYS = {'key_1', 'key_2', 'key_3', 'key_4'}


class UserTraitSchema(Schema):
    user_id = fields.Int(validate=validate.Range(min=1))
    trait_key = fields.Str(validate=lambda x: x in USER_TERM_KEYS)
    trait_value = fields.Str(validate=validate.Length(min=1, max=255))


class UserTrait(BaseModel):
    __tablename__ = 'users_traits'
    __table_args__ = (db.UniqueConstraint('user_id', 'trait_key', name='users_traits_ukey'),)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), index=True)
    trait_key = db.Column(db.String(40), index=True, nullable=False)
    trait_value = db.Column(db.String(255), nullable=True)

    def __init__(self, user_id, trait_key, trait_value):
        self.user_id = user_id
        self.trait_key = trait_key
        self.trait_value = trait_value

    @classmethod
    def set_trait(cls, user_id, trait_key, trait_value):
        user_trait = cls.query.filter_by(user_id=user_id, trait_key=trait_key).first()
        if user_trait:
            user_trait.trait_value = trait_value
            user_trait.deleted = 0
        else:
            user_trait = cls(user_id, trait_key, trait_value)
        return user_trait


@db.event.listens_for(UserTrait, 'before_insert')
def before_insert_user_trait(mapper, connect, user_trait):
    UserTraitSchema().load({
        'user_id': user_trait.user_id,
        'trait_key': user_trait.trait_key,
        'trait_value': user_trait.trait_value,
    })

    if UserTrait.query.filter_by(user_id=user_trait.user_id, trait_key=user_trait.trait_key).first():
        raise ValidationError({'trait_key': ['Already exists.']})


@db.event.listens_for(UserTrait, 'before_update')
def before_update_user(mapper, connect, user_trait):
    UserTraitSchema().load({
        'user_id': user_trait.user_id,
        'trait_key': user_trait.trait_key,
        'trait_value': user_trait.trait_value,
    })
