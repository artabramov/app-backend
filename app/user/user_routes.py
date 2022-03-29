from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from app import app, db, log
from app.core.response import response
from app.user.user_schema import UserSchema
from app.user.user_model import UserModel
from marshmallow import ValidationError
from werkzeug.exceptions import Conflict


@app.route('/user/', methods=['POST'])
def user_post():
    user_email = request.args.get('user_email', '')
    user_name = request.args.get('user_name', '')
    user_pass = request.args.get('user_pass', '')
    user_status = 'pending'

    try:
        UserSchema().load({
            'user_email': user_email,
            'user_name': user_name,
            'user_pass': user_pass,
            'user_status': user_status,
        })
    except ValidationError as e:
        return response({}, e.messages, 400)

    try:
        user = UserModel(user_email, user_name, user_pass, user_status)
        db.session.add(user)
        db.session.flush()
        db.session.commit()
    except Conflict as e:
        return response({}, e.description, 409)
    except SQLAlchemyError as e:
        log.error(e.orig.msg)
        db.session.rollback()
        return response({}, {'db': ['Internal Server Error']}, 500)

    return response({'user': {'id': user.id}}, {}, 201)