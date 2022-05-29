from flask import request
from app import app, log
from app.user import user_handlers
from multiprocessing import Process
from multiprocessing import Manager
from app.core.app_response import app_response
from app.core.async_upload import async_upload
from app.user.user_handlers import user_exists, user_insert, user_select, user_update, user_delete, user_auth
from app.user.user_handlers import qrcode_create, qrcode_remove
from app.user.user import TOTP_ATTEMPTS_LIMIT


# user register
@app.route('/user/', methods=['POST'], endpoint='user_register')
@app_response
def user_register():
    user_login = request.args.get('user_login', '')
    user_name = request.args.get('user_name', '')
    user_pass = request.args.get('user_pass', '')
    user_role = 'guest' if user_exists(user_role='admin', deleted=0) else 'admin'
    user_meta = {
        'key_1': 'value 1',
        'key_2': 'value 2',
        'key_3': 'value 3',
    }

    this_user = user_insert(user_login, user_name, user_pass, user_role, user_meta)
    qrcode_create(this_user.totp_key, this_user.user_login)

    return {
        'totp_key': this_user.totp_key, 
        'totp_qrcode': app.config['QRCODES_URI'] % this_user.totp_key
    }, {}, 201


# user signin
@app.route('/token/', methods=['GET'], endpoint='user_signin')
@app_response
def user_signin():
    user_login = request.args.get('user_login', '')
    user_totp = request.args.get('user_totp', '')

    this_user = user_select(user_login=user_login, deleted=0)
    if not this_user:
        return {}, {'user_login': ['user_login is not found'], }, 404

    elif this_user.totp_attempts >= TOTP_ATTEMPTS_LIMIT:
        return {}, {'user_totp': ['user_totp attempts are over'], }, 406

    elif user_totp == this_user.user_totp:
        qrcode_remove(this_user.user_totp)
        user_update(this_user, totp_attempts=0)
        return {'user_token': this_user.user_token}, {}, 200

    else:
        totp_attempts = this_user.totp_attempts + 1
        user_update(this_user, totp_attempts=totp_attempts)
        return {}, {'user_totp': ['user_totp is incorrect'], }, 404


# user signout
@app.route('/token/', methods=['PUT'], endpoint='user_signout')
@app_response
def user_signout():
    user_token = request.headers.get('user_token')

    this_user = user_auth(user_token)
    token_signature = this_user.generate_token_signature()
    user_update(this_user, token_signature=token_signature)
    return {}, {}, 200









# user restore
@app.route('/pass/', methods=['GET'])
def _user_restore():
    user_login = request.args.get('user_login', '')
    user_pass = request.args.get('user_pass', '')
    return user_handlers.user_restore(user_login, user_pass)


# user select
@app.route('/user/<user_id>', methods=['GET'])
def _user_select(user_id):
        user_token = request.headers.get('user_token')
        return user_handlers.user_select(user_token, user_id)


# user update
@app.route('/user/<user_id>', methods=['PUT'])
def _user_update(user_id):
    user_token = request.headers.get('user_token', None)
    user_id = int(user_id)
    user_name = request.args.get('user_name', None)
    user_role = request.args.get('user_role', None)
    user_pass = request.args.get('user_pass', None)

    props_data = {}
    if request.args.get('key_1', False): 
        props_data['key_1'] = request.args.get('key_1')
    if request.args.get('key_2', False): 
        props_data['key_2'] = request.args.get('key_2')

    return user_handlers.user_update(user_token, user_id, user_name, user_role, user_pass, props_data)


# user delete
@app.route('/user/<user_id>', methods=['DELETE'])
def _user_remove(user_id):
    user_token = request.headers.get('user_token', None)
    user_id = int(user_id)

    return user_handlers.user_delete(user_token, user_id)




# user image upload
@app.route('/image/', methods=['POST'], endpoint='image_post')
@app_response
def _image_post():
    user_token = request.headers.get('user_token', None)
    user_files = request.files.getlist('user_files')
    uploaded_files = []

    """
    for user_file in user_files:
        uploaded_file = file_upload(user_file, '/app/images/', ['image/jpeg'])
        uploaded_files.append(uploaded_file)
    """

    manager = Manager()
    uploaded_files = manager.list()

    jobs = []
    for user_file in user_files:
        job = Process(target=async_upload, args=(user_file, '/app/images/', ['image/jpeg'], uploaded_files))
        jobs.append(job)
        job.start()
    
    for job in jobs:
        job.join()

    return {}, {'files': list(uploaded_files), }, 200








"""
# user restore
@app.route('/pass/', methods=['GET'])
def pass_get():
    try:
        user_login = request.args.get('user_login', '')
        user_pass = request.args.get('user_pass', '')
        async_result = user_restore.apply_async(args=[user_login, user_pass], task_id=g.request_context.uuid).get(timeout=10)
        return app_response(*async_result)

    except TimeoutError as e:
        log.error(e)
        return app_response({}, {'db': ['Gateway Timeout']}, 504)


# user signin
@app.route('/token/', methods=['GET'])
def token_get():
    try:
        user_login = request.args.get('user_login', '')
        user_code = request.args.get('user_code', '')
        async_result = user_signin.apply_async(args=[user_login, user_code], task_id=g.request_context.uuid).get(timeout=10)
        return app_response(*async_result)

    except TimeoutError as e:
        log.error(e)
        return app_response({}, {'db': ['Gateway Timeout']}, 504)


# user signout
@app.route('/token/', methods=['PUT'])
def token_put():
    try:
        user_token = request.headers.get('user_token')
        async_result = user_signout.apply_async(args=[user_token], task_id=g.request_context.uuid).get(timeout=10)
        return app_response(*async_result)

    except TimeoutError as e:
        log.error(e)
        return app_response({}, {'db': ['Gateway Timeout']}, 504)


# user select
@app.route('/user/<user_id>', methods=['GET'])
def user_get(user_id):
    try:
        user_token = request.headers.get('user_token')
        async_result = user_select.apply_async(args=[user_token, user_id], task_id=g.request_context.uuid).get(timeout=10)
        return app_response(*async_result)

    except TimeoutError as e:
        log.error(e)
        return app_response({}, {'db': ['Gateway Timeout']}, 504)


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
        return app_response(*async_result)

    except TimeoutError as e:
        log.error(e)
        return app_response({}, {'db': ['Gateway Timeout']}, 504)


# user delete
@app.route('/user/<user_id>', methods=['DELETE'])
def user_delete(user_id):
    try:
        user_id = int(user_id)
        user_token = request.headers.get('user_token', None)

        async_result = user_remove.apply_async(args=[user_token, user_id], task_id=g.request_context.uuid).get(timeout=10)
        return app_response(*async_result)

    except TimeoutError as e:
        log.error(e)
        return app_response({}, {'db': ['Gateway Timeout']}, 504)


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
        return app_response(*async_result)

    except Exception as e:
        log.error(e)
        return app_response({}, {'db': ['Internal Server Error']}, 504)

    except TimeoutError as e:
        log.error(e)
        return app_response({}, {'db': ['Gateway Timeout']}, 504)




    user_file = request.files.get('user_file', None)

    if not user_file or not getattr(user_file, 'filename'):
        return app_response({}, {'user_file': ['Where is the file?']}, 504)

    file_ext = user_file.filename.rsplit('.', 1)[1].lower()

    if file_ext not in app.config['USER_IMAGES_EXTENSIONS']:
        return app_response({}, {'user_file': ['Extebsion is incorrect']}, 504)

    file_name = os.path.join(app.config['USER_IMAGES_PATH'], str(uuid.uuid4()) + file_ext)
    user_file.save(file_name)
    file_size = os.path.getsize(file_name)
    file_mime = user_file.mimetype
    return app_response({}, {}, 200)
"""

