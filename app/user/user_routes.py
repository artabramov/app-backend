from flask import request
from app import app, log
from app.user import user_handlers
from multiprocessing import Process
from multiprocessing import Manager
from app.core.app_response import app_response
from app.core.async_upload import async_upload
from app.user.user_handlers import user_exists, user_insert, user_select, user_update, user_delete, user_auth
from app.user.user_handlers import qrcode_create, qrcode_remove
from app.user.user import PASS_ATTEMPTS_LIMIT, PASS_SUSPEND_TIME, TOTP_ATTEMPTS_LIMIT
from app.user.user import User
import time


@app.route('/user/', methods=['POST'], endpoint='user_post')
@app_response
def user_post():
    """ User register """
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


@app.route('/token/', methods=['GET'], endpoint='token_get')
@app_response
def token_get():
    """ User signin """
    user_login = request.args.get('user_login', '')
    user_totp = request.args.get('user_totp', '')

    this_user = user_select(user_login=user_login, deleted=0)
    if not this_user:
        return {}, {'user_login': ['user_login not found'], }, 404

    elif this_user.totp_attempts >= TOTP_ATTEMPTS_LIMIT:
        return {}, {'user_totp': ['user_totp attempts are over'], }, 406

    elif user_totp == this_user.user_totp:
        qrcode_remove(this_user.totp_key)
        user_update(this_user, totp_attempts=0)
        return {'user_token': this_user.user_token}, {}, 200

    else:
        totp_attempts = this_user.totp_attempts + 1
        user_update(this_user, totp_attempts=totp_attempts)
        return {}, {'user_totp': ['user_totp is incorrect'], }, 404


@app.route('/token/', methods=['PUT'], endpoint='token_put')
@app_response
def token_put():
    """ User signout """
    user_token = request.headers.get('user_token')

    this_user = user_auth(user_token)
    token_signature = this_user.generate_token_signature()
    user_update(this_user, token_signature=token_signature)
    return {}, {}, 200


@app.route('/pass/', methods=['GET'], endpoint='pass_get')
@app_response
def pass_get():
    """ User restore """
    user_login = request.args.get('user_login', '').lower()
    user_pass = request.args.get('user_pass', '')
    pass_hash = User.get_pass_hash(user_login + user_pass)

    this_user = user_select(user_login=user_login, deleted=0)
    if not this_user:
        return {}, {'user_login': ['user_login not found'], }, 404

    elif this_user.pass_suspended > time.time():
        return {}, {'user_pass': ['user_pass temporarily suspended'], }, 406

    elif this_user.pass_hash == pass_hash:
        user_update(this_user, pass_attempts=0, pass_suspended=0, totp_attempts=0)
        return {}, {}, 200

    else:
        pass_attempts = this_user.pass_attempts + 1
        pass_suspended = 0
        if pass_attempts >= PASS_ATTEMPTS_LIMIT:
            pass_attempts = 0
            pass_suspended = time.time() + PASS_SUSPEND_TIME

        user_update(this_user, pass_attempts=pass_attempts, pass_suspended=pass_suspended)
        return {}, {'user_pass': ['user_pass is incorrect'], }, 406


@app.route('/user/<user_id>', methods=['GET'], endpoint='user_get')
@app_response
def user_get(user_id):
    """ User select """
    if not user_id.isnumeric():
        return {}, {'user_id': ['user_id is incorrect']}, 404

    user_id = int(user_id)
    user_token = request.headers.get('user_token')

    this_user = user_auth(user_token)
    user = user_select(id=user_id)

    if user:
        return {'user': {
            'id': user.id,
            'is_deleted': user.is_deleted,
            'user_name': user.user_name,
            'meta': {meta.meta_key: meta.meta_value for meta in user.meta}    
        }}, {}, 200

    else:
        return {}, {'user_id': ['user_id not found']}, 404


@app.route('/user/<user_id>', methods=['PUT'], endpoint='user_put')
@app_response
def user_put(user_id):
    """ User update """
    if not user_id.isnumeric():
        return {}, {'user_id': ['user_id is incorrect']}, 404

    user_id = int(user_id)
    user_token = request.headers.get('user_token')
    user_name = request.args.get('user_name', None)
    user_role = request.args.get('user_role', None)
    user_pass = request.args.get('user_pass', None)

    this_user = user_auth(user_token)
    user = user_select(id=user_id)

    if not user:
        return {}, {'user_id': ['user_id not found']}, 404

    elif this_user.id == user.id or this_user.can_admin:
        user_data = {}
        if user_name:
            user_data['user_name'] = user_name

        if user_pass:
            user_data['user_pass'] = user_pass

        if user_role and this_user.can_admin and this_user.id != user.id:
            user_data['user_role'] = user_role

        user_data['user_meta'] = {
            'key_1': 'value 111', 
            'key_2': 'None', 
            'key_4': 'value 44'}

        user_update(user, **user_data)
        return {}, {}, 200

    else:
        return {}, {'user_id': ['user_id update forbidden'], }, 403


@app.route('/user/<user_id>', methods=['DELETE'], endpoint='user_del')
@app_response
def user_del(user_id):
    """ User delete """
    if not user_id.isnumeric():
        return {}, {'user_id': ['user_id is incorrect']}, 404

    user_id = int(user_id)
    user_token = request.headers.get('user_token')

    this_user = user_auth(user_token)
    user = user_select(id=user_id)

    if not user:
        return {}, {'user_id': ['user_id not found']}, 404

    elif this_user.id != user.id and this_user.can_admin:
        user_delete(user)
        return {}, {}, 200

    else:
        return {}, {'user_id': ['user_id delete forbidden'], }, 403


@app.route('/image/', methods=['POST'], endpoint='files_post')
@app_response
def files_post():
    """ Files upload """
    user_token = request.headers.get('user_token', None)
    user_files = request.files.getlist('user_files')

    this_user = user_auth(user_token)

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
@app.route('/image/', methods=['POST'], endpoint='_image_post')
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








