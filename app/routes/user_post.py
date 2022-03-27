from flask import request, jsonify
from app import app, db
from app.schemas.user_schema import UserSchema
from marshmallow import ValidationError


@app.route('/user/', methods=['POST'])
def user_post():

    try:
        UserSchema().load({
            'user_name': request.args.get('user_name', None),
            'user_pass': request.args.get('user_pass', None)
        })
    except ValidationError as e:
        pass

    return jsonify({
        'user_name': request.args.get('user_name', None),
        'user_pass': request.args.get('user_pass', None)
    })