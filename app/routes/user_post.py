from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from app import app, db
from app.core.response import response
from app.schemas.user_schema import UserSchema
from app.models.user_model import UserModel
from marshmallow import ValidationError


@app.route('/user/', methods=['POST'])
def user_post():
    user_email = request.args.get('user_email', '')
    user_name = request.args.get('user_name', '')
    user_pass = request.args.get('user_pass', '')

    try:
        UserSchema().load({
            'user_email': user_email,
            'user_name': user_name,
            'user_pass': user_pass
        })
    except ValidationError as e:
        return response({}, e.messages, 500)

    try:
        user = UserModel(user_email, user_name, user_pass)
        db.session.add(user)
        db.session.flush()
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return response({}, {'db': ['db error']}, 500)

    return response({'user': {'id': user.id}}, {}, 200)