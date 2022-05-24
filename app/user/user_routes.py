from flask import request
from app import app, log
#from werkzeug.utils import secure_filename
#from app.core.file_upload import file_upload
#from app.core.file_read import file_read
from app.user import user_handlers


# user register
@app.route('/user/', methods=['POST'])
def user_register():
    user_login = request.args.get('user_login', '')
    user_name = request.args.get('user_name', '')
    user_pass = request.args.get('user_pass', '')
    meta_data = {
        'meta_key_1': 'meta value 1',
        'meta_key_2': 'meta value 2',
        'meta_key_3': 'meta value 3',
    }
    return user_handlers.user_register(user_login, user_name, user_pass, meta_data)


# user signin
@app.route('/token/', methods=['GET'])
def user_signin():
    user_login = request.args.get('user_login', '')
    user_code = request.args.get('user_code', '')
    return user_handlers.user_signin(user_login, user_code)


# user signout
@app.route('/token/', methods=['PUT'])
def user_signout():
    user_token = request.headers.get('user_token')
    return user_handlers.user_signout(user_token)


# user restore
@app.route('/pass/', methods=['GET'])
def user_restore():
    user_login = request.args.get('user_login', '')
    user_pass = request.args.get('user_pass', '')
    return user_handlers.user_restore(user_login, user_pass)


# user select
@app.route('/user/<user_id>', methods=['GET'])
def user_select(user_id):
        user_token = request.headers.get('user_token')
        return user_handlers.user_select(user_token, user_id)




"""
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
        #user_file = request.files.get('user_file', None)
        user_file = request.files['user_file']
        file_bytes = user_file.read()

        file_data = file_upload(user_file, app.config['USER_IMAGES_PATH'], app.config['USER_IMAGES_EXTENSIONS'])
        file_tmp = file_read(user_file)

        async_result = image_upload.apply_async(args=[user_token, file_data, request.files], task_id=g.request_context.uuid).get(timeout=10)
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
"""

