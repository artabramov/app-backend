from flask import request
from sqlalchemy.exc import SQLAlchemyError
from app import app, db, log
from app.core.response import response
from app.user.user_schema import UserSchema
from app.user.user_model import UserModel
from app.user.user_tasks import user_insert
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


@app.route('/user/<int:user_id>', methods=['GET'])
def user_get(user_id):
    try:
        user = UserModel.query.filter_by(id=user_id).first()

    except SQLAlchemyError as e:
        log.error(e.orig.msg)
        db.session.rollback()
        return response({}, {'db': ['Internal Server Error']}, 500)

    if not user:
        return response({}, {'id': ['Not Found']}, 404)

    return response({'user': {'id': user.id, 'user_email': user.user_email}}, {}, 200)


@app.route('/user2/', methods=['POST'])
def user_post2():
    user_email = request.args.get('user_email', '')
    user_name = request.args.get('user_name', '')
    user_pass = request.args.get('user_pass', '')

    async_result = user_insert.apply_async(args=[
        user_email, user_pass, user_name
    ]).get(timeout=10)

    return response(async_result)
