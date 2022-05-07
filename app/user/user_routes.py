from flask import request, g
from app import app, log
from app.core.json_response import json_response
from app.user.user_tasks import user_register, user_restore, user_signin, user_signout, user_select, user_update, user_remove
from celery.exceptions import TimeoutError
from app.user_meta.user_meta_schema import USER_META_KEYS


# user register
@app.route('/user/', methods=['POST'])
def user_post():
    try:
        user_login = request.args.get('user_login', '')
        user_name = request.args.get('user_name', '')
        user_pass = request.args.get('user_pass', '')

        meta_data = {}
        for meta_key in USER_META_KEYS:
            meta_value = request.args.get(meta_key, None)
            if meta_value:
                meta_data[meta_key] = meta_value

        async_result = user_register.apply_async(args=[
            user_login, user_name, user_pass, meta_data
        ], task_id=g.request_context.uuid).get(timeout=10)
        return json_response(*async_result)

    except TimeoutError as e:
        log.error(e)
        return json_response({}, {'db': ['Gateway Timeout']}, 504)


# user restore
@app.route('/pass/', methods=['GET'])
def pass_get():
    try:
        user_login = request.args.get('user_login', '')
        user_pass = request.args.get('user_pass', '')
        async_result = user_restore.apply_async(args=[user_login, user_pass], task_id=g.request_context.uuid).get(timeout=10)
        return json_response(*async_result)

    except TimeoutError as e:
        log.error(e)
        return json_response({}, {'db': ['Gateway Timeout']}, 504)


# user signin
@app.route('/token/', methods=['GET'])
def token_get():
    try:
        user_login = request.args.get('user_login', '')
        user_code = request.args.get('user_code', '')
        async_result = user_signin.apply_async(args=[user_login, user_code], task_id=g.request_context.uuid).get(timeout=10)
        return json_response(*async_result)

    except TimeoutError as e:
        log.error(e)
        return json_response({}, {'db': ['Gateway Timeout']}, 504)


# user signout
@app.route('/token/', methods=['PUT'])
def token_put():
    try:
        user_token = request.headers.get('user_token')
        async_result = user_signout.apply_async(args=[user_token], task_id=g.request_context.uuid).get(timeout=10)
        return json_response(*async_result)

    except TimeoutError as e:
        log.error(e)
        return json_response({}, {'db': ['Gateway Timeout']}, 504)


# user select
@app.route('/user/<user_id>', methods=['GET'])
def user_get(user_id):
    try:
        user_token = request.headers.get('user_token')
        async_result = user_select.apply_async(args=[user_token, user_id], task_id=g.request_context.uuid).get(timeout=10)
        return json_response(*async_result)

    except TimeoutError as e:
        log.error(e)
        return json_response({}, {'db': ['Gateway Timeout']}, 504)


# user update
@app.route('/user/<user_id>', methods=['PUT'])
def user_put(user_id):
    try:
        user_id = int(user_id)
        user_token = request.headers.get('user_token', None)
        user_name = request.args.get('user_name', None)
        user_role = request.args.get('user_role', None)
        user_pass = request.args.get('user_pass', None)

        meta_data = {}
        for meta_key in USER_META_KEYS:
            meta_value = request.args.get(meta_key, None)
            if meta_value:
                meta_data[meta_key] = meta_value

        async_result = user_update.apply_async(args=[user_token, user_id, user_name, user_role, user_pass, meta_data], task_id=g.request_context.uuid).get(timeout=10)
        return json_response(*async_result)

    except TimeoutError as e:
        log.error(e)
        return json_response({}, {'db': ['Gateway Timeout']}, 504)


# user delete
@app.route('/user/<user_id>', methods=['DELETE'])
def user_delete(user_id):
    try:
        user_id = int(user_id)
        user_token = request.headers.get('user_token', None)

        async_result = user_remove.apply_async(args=[user_token, user_id], task_id=g.request_context.uuid).get(timeout=10)
        return json_response(*async_result)

    except TimeoutError as e:
        log.error(e)
        return json_response({}, {'db': ['Gateway Timeout']}, 504)




def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['USER_IMAGES_EXTENSIONS']


# user image upload
@app.route('/image/', methods=['POST'])
def image_post():
    from werkzeug.utils import secure_filename
    #from flask import url_for
    import os
    import uuid

    if 'file' not in request.files:
        return json_response({}, {'image': ['where is the file? 1']}, 504)

    file = request.files['file']
    if file.filename == '':
        return json_response({}, {'image': ['where is the file? 2']}, 504)

    if file and allowed_file(file.filename):
        file_source = secure_filename(file.filename)
        file_ext = os.path.splitext(file_source)[1]
        file_name = str(uuid.uuid4()) + file_ext
        file_mime = file.mimetype
        file_path = os.path.join(app.config['USER_IMAGES_PATH'], file_name)

        file.save(file_path)
        file_size = os.path.getsize(file_path)

        """
        meta_key = 'user_image'
        meta_value = file_path
        
        user_meta = UserMetaModel.query.filter_by(user_id=user_id, meta_key=meta_key).first()
        if user_meta:
            user_meta.meta_value = meta_value
        else:
            user_meta = UserMetaModel(authed_user.id, meta_key, meta_value)
        db.session.add(user_meta)
        db.session.flush()

        db.session.commit()
        cache.set('user.%s' % (user.id), user)
        """

        return json_response({}, {'file': str(file)}, 200)

    return json_response({}, {}, 200)

