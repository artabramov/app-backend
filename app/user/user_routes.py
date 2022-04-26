from flask import request, g
from sqlalchemy.exc import SQLAlchemyError
from app import app, db, log
from app.core.response import response
from app.user.user_schema import UserSchema
from app.user.user_model import UserModel
from app.user.user_tasks import user_register, user_restore, user_login, user_logout, user_select, user_update
from marshmallow import ValidationError
from celery.exceptions import TimeoutError

# register user
@app.route('/user/', methods=['POST'])
def user_post():
    user_email = request.args.get('user_email', '')
    user_name = request.args.get('user_name', '')

    try:
        async_result = user_register.apply_async(args=[
            user_email, user_name
        ], task_id=g.request_context.uuid).get(timeout=10)
        return response(*async_result)

    except TimeoutError as e:
        log.error(e)
        return response({}, {'db': ['Gateway Timeout']}, 504)


# user restore
@app.route('/pass/', methods=['GET'])
def pass_get():
    try:
        user_email = request.args.get('user_email', '')
        async_result = user_restore.apply_async(args=[user_email], task_id=g.request_context.uuid).get(timeout=10)
        return response(*async_result)

    except TimeoutError as e:
        log.error(e)
        return response({}, {'db': ['Gateway Timeout']}, 504)


# user login
@app.route('/token/', methods=['GET'])
def token_get():
    try:
        log.debug('bla bla bla')
        user_email = request.args.get('user_email', '')
        user_pass = request.args.get('user_pass', '')
        async_result = user_login.apply_async(args=[user_email, user_pass], task_id=g.request_context.uuid).get(timeout=10)
        return response(*async_result)

    except TimeoutError as e:
        log.error(e)
        return response({}, {'db': ['Gateway Timeout']}, 504)


# user logout
@app.route('/token/', methods=['PUT'])
def token_put():
    try:
        user_token = request.headers.get('user_token')
        async_result = user_logout.apply_async(args=[user_token], task_id=g.request_context.uuid).get(timeout=10)
        return response(*async_result)

    except TimeoutError as e:
        log.error(e)
        return response({}, {'db': ['Gateway Timeout']}, 504)


# select user
@app.route('/user/<user_id>', methods=['GET'])
def user_get(user_id):
    try:
        user_token = request.headers.get('user_token')
        async_result = user_select.apply_async(args=[user_token, user_id], task_id=g.request_context.uuid).get(timeout=10)
        return response(*async_result)

    except TimeoutError as e:
        log.error(e)
        return response({}, {'db': ['Gateway Timeout']}, 504)


# update user
@app.route('/user/<user_id>', methods=['PUT'])
def user_put(user_id):
    try:
        user_id = int(user_id)
        user_token = request.headers.get('user_token', None)
        user_name = request.args.get('user_name', None)
        async_result = user_update.apply_async(args=[user_token, user_id, user_name], task_id=g.request_context.uuid).get(timeout=10)
        #async_result = user_update(user_token, user_id, user_name, is_admin)
        return response(*async_result)

    except TimeoutError as e:
        log.error(e)
        return response({}, {'db': ['Gateway Timeout']}, 504)
