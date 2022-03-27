from flask import request, jsonify
from app import app, db


@app.route('/user/', methods=['POST'])
def user_post():
    return jsonify({
        'user_email': request.args.get('user_email', None),
        'user_password': request.args.get('user_password', None),
        'user_name': request.args.get('user_name', None)
    })