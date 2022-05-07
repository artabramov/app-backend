from flask import request, g
from app import app, log
from app.core.json_response import json_response
from app.user.user_tasks import user_register, user_restore, user_signin, user_signout, user_select, user_update, user_remove, image_upload
from celery.exceptions import TimeoutError
from app.user_meta.user_meta_schema import USER_META_KEYS
from werkzeug.utils import secure_filename
from app.core.file_upload import file_upload


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
    try:
        user_token = request.headers.get('user_token', None)
        user_file = request.files.get('user_file', None)
        file_data = file_upload(user_file, app.config['USER_IMAGES_PATH'], app.config['USER_IMAGES_EXTENSIONS'])

        """
        filename_src = getattr(user_file, 'filename', None)
        if not user_file or not filename_src:
            return json_response({}, {'user_file': ['Where is the file?']}, 406)

        file_ext = user_file.filename.rsplit('.', 1)[1].lower()
        if file_ext not in app.config['USER_IMAGES_EXTENSIONS']:
            return json_response({}, {'user_file': ['Extension is incorrect']}, 406)

        filename_dst = os.path.join(app.config['USER_IMAGES_PATH'], str(uuid.uuid4()) + '.' + file_ext)
        user_file.save(filename_dst)
        file_data = {
            'filename_src': filename_src,
            'filename_dst': filename_dst,
            'file_size': os.path.getsize(filename_dst),
            'file_mime': user_file.mimetype,
            'file_ext': file_ext,
        }
        """

        async_result = image_upload.apply_async(args=[user_token, file_data], task_id=g.request_context.uuid).get(timeout=10)
        return json_response(*async_result)

    except Exception as e:
        log.error(e)
        return json_response({}, {'db': ['Internal Server Error']}, 504)

    except TimeoutError as e:
        log.error(e)
        return json_response({}, {'db': ['Gateway Timeout']}, 504)




    user_file = request.files.get('user_file', None)

    if not user_file or not getattr(user_file, 'filename'):
        return json_response({}, {'user_file': ['Where is the file?']}, 504)

    file_ext = user_file.filename.rsplit('.', 1)[1].lower()

    if file_ext not in app.config['USER_IMAGES_EXTENSIONS']:
        return json_response({}, {'user_file': ['Extebsion is incorrect']}, 504)

    file_name = os.path.join(app.config['USER_IMAGES_PATH'], str(uuid.uuid4()) + file_ext)
    user_file.save(file_name)
    file_size = os.path.getsize(file_name)
    file_mime = user_file.mimetype
    return json_response({}, {}, 200)


