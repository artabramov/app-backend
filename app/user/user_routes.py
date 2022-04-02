from flask import request
from sqlalchemy.exc import SQLAlchemyError
from app import app, db, log
from app.core.response import response
from app.user.user_schema import UserSchema
from app.user.user_model import UserModel
from app.user.user_tasks import user_insert, user_select
from marshmallow import ValidationError
from celery.exceptions import TimeoutError


@app.route('/user/<user_id>', methods=['GET'])
def user_get(user_id):
    try:
        async_result = user_select.apply_async(args=[user_id]).get(timeout=10)
        return response(*async_result)

    except TimeoutError as e:
        log.critical(e)
        return response({}, {'db': ['Gateway Timeout']}, 504)

    """
    try:
        user = UserModel.query.filter_by(id=user_id).first()

    except SQLAlchemyError as e:
        log.error(e.orig.msg)
        db.session.rollback()
        return response({}, {'db': ['Internal Server Error']}, 500)

    if not user:
        return response({}, {'id': ['Not Found']}, 404)

    return response({'user': {'id': user.id, 'user_email': user.user_email}}, {}, 200)
    """


@app.route('/user/', methods=['POST'])
def user_post():
    user_email = request.args.get('user_email', '')
    user_name = request.args.get('user_name', '')
    user_pass = request.args.get('user_pass', '')

    try:
        async_result = user_insert.apply_async(args=[
            user_email, user_pass, user_name
        ]).get(timeout=10)
        return response(*async_result)

    except TimeoutError as e:
        log.critical(e)
        return response({}, {'db': ['Gateway Timeout']}, 504)

    
