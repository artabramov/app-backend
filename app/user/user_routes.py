from flask import request, g
from sqlalchemy.exc import SQLAlchemyError
from app import app, db, log
from app.core.response import response
from app.user.user_schema import UserSchema
from app.user.user_model import UserModel
from app.user.user_tasks import user_register, user_select
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




"""
# user login
@app.route('/token/', methods=['GET'])
def token_get(user_id):
    try:
        async_result = user_login.apply_async(args=[user_id], task_id=g.request_context.uuid).get(timeout=10)
        return response(*async_result)

    except TimeoutError as e:
        log.error(e)
        return response({}, {'db': ['Gateway Timeout']}, 504)
"""


# select user
@app.route('/user/<user_id>', methods=['GET'])
def user_get(user_id):
    try:
        async_result = user_select.apply_async(args=[user_id], task_id=g.request_context.uuid).get(timeout=10)
        return response(*async_result)

    except TimeoutError as e:
        log.error(e)
        return response({}, {'db': ['Gateway Timeout']}, 504)







    
