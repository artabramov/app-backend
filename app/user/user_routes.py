from flask import request
from app import app, log
from app.user import user_handlers
from multiprocessing import Process
from multiprocessing import Manager
from app.core.app_response import app_response
from app.core.upload_file import upload_file
from app.user.user_handlers import user_exists, user_insert, user_select, user_update, user_delete, user_auth
from app.user.user import PASS_ATTEMPTS_LIMIT, PASS_SUSPEND_TIME, TOTP_ATTEMPTS_LIMIT, TOKEN_EXPIRATION_TIME
from app.user.user import User
import time

from app.core.basic_handlers import insert, update, delete, select, select_all
from app.core.user_auth import user_auth
from app.core.qrcode_handlers import qrcode_make, qrcode_remove
from flask import g

QRCODE_URI = app.config['QRCODE_URI']


@app.route('/user/', methods=['POST'], endpoint='user_register')
@app_response
def user_register():
    user_login = request.args.get('user_login', '').lower()
    user_name = request.args.get('user_name', '')
    user_pass = request.args.get('user_pass', '')
    user_meta = {
        'remote_addr': request.remote_addr,
        'user_agent': request.headers.get('User-Agent'),
    }

    user = insert(User, user_login=user_login, user_name=user_name, user_pass=user_pass, meta=user_meta)
    qrcode_make(user.totp_key, user.user_login)

    return {
        'totp_key': user.totp_key, 
        'totp_qrcode': QRCODE_URI % user.totp_key
    }, {}, 201


@app.route('/token/', methods=['GET'], endpoint='user_signin')
@app_response
def user_signin():
    user_login = request.args.get('user_login', '').lower()
    user_totp = request.args.get('user_totp', '')

    user = select(User, user_login=user_login, deleted=0)
    if not user:
        return {}, {'user_login': ['user not found or deleted'], }, 404

    elif user.totp_attempts >= TOTP_ATTEMPTS_LIMIT:
        return {}, {'user_totp': ['user_totp attempts are over'], }, 406

    elif user_totp == user.user_totp:
        qrcode_remove(user.totp_key)
        token_expires = time.time() + TOKEN_EXPIRATION_TIME
        update(user, totp_attempts=0, token_expires=token_expires)
        return {'user_token': user.user_token}, {}, 200

    else:
        totp_attempts = user.totp_attempts + 1
        update(user, totp_attempts=totp_attempts)
        return {}, {'user_totp': ['user_totp is incorrect'], }, 404


@app.route('/token/', methods=['PUT'], endpoint='user_signout')
@app_response
@user_auth
def user_signout():
    token_signature = g.user.generate_token_signature()
    update(g.user, token_signature=token_signature)
    return {}, {}, 200


@app.route('/pass/', methods=['GET'], endpoint='user_restore')
@app_response
def user_restore():
    user_login = request.args.get('user_login', '').lower()
    user_pass = request.args.get('user_pass', '')
    pass_hash = User.get_pass_hash(user_login + user_pass)

    user = select(User, user_login=user_login, deleted=0)
    if not user:
        return {}, {'user_login': ['user_login not found'], }, 404

    elif user.pass_suspended > time.time():
        return {}, {'user_pass': ['user_pass temporarily suspended'], }, 406

    elif user.pass_hash == pass_hash:
        update(user, pass_attempts=0, pass_suspended=0, totp_attempts=0)
        return {}, {}, 200

    else:
        pass_attempts = user.pass_attempts + 1
        pass_suspended = 0
        if pass_attempts >= PASS_ATTEMPTS_LIMIT:
            pass_attempts = 0
            pass_suspended = time.time() + PASS_SUSPEND_TIME

        update(user, pass_attempts=pass_attempts, pass_suspended=pass_suspended)
        return {}, {'user_pass': ['user_pass is incorrect'], }, 406


@app.route('/user/<int:user_id>', methods=['GET'], endpoint='user_select')
@app_response
@user_auth
def user_select(user_id):
    user = select(User, id=user_id)

    if user:
        return {'user': {
            'id': user.id,
            'is_deleted': user.is_deleted,
            'user_name': user.user_name,
            'meta': {meta.meta_key: meta.meta_value for meta in user.meta}    
        }}, {}, 200

    else:
        return {}, {'user_id': ['user_id not found']}, 404


@app.route('/user/<int:user_id>', methods=['PUT'], endpoint='user_update')
@app_response
@user_auth
def user_update(user_id):
    user_name = request.args.get('user_name', '')
    user_role = request.args.get('user_role', '')
    user_pass = request.args.get('user_pass', '')

    user = select(User, id=user_id)

    if not user:
        return {}, {'user_id': ['user_id not found']}, 404

    elif g.user.id == user.id or g.user.can_admin:
        user_data = {}
        if user_name:
            user_data['user_name'] = user_name

        if user_pass:
            user_data['user_pass'] = user_pass

        if user_role and g.user.can_admin and g.user.id != user.id:
            user_data['user_role'] = user_role

        update(user, **user_data)
        return {}, {}, 200

    else:
        return {}, {'user_id': ['user_id update forbidden'], }, 403


@app.route('/user/<int:user_id>', methods=['DELETE'], endpoint='user_delete')
@app_response
@user_auth
def user_delete(user_id):
    user = select(User, id=user_id)

    if not user:
        return {}, {'user_id': ['user_id not found']}, 404

    elif g.user.id != user.id and g.user.can_admin:
        delete(user)
        return {}, {}, 200

    else:
        return {}, {'user_id': ['user_id delete forbidden'], }, 403


@app.route('/image/', methods=['POST'], endpoint='user_image')
@app_response
@user_auth
def user_image():
    user_file = request.files.getlist('user_file')[0]
    manager = Manager()
    uploaded_files = manager.list() # do not rename this variable

    jobs = []
    job = Process(target=upload_file, args=(user_file, '/app/images/', ['image/jpeg'], uploaded_files))
    jobs.append(job)
    job.start()
    
    for job in jobs:
        job.join()

    uploaded_file = uploaded_files[0]
    user_meta = {'user_image': uploaded_file['file_path']}
    update(g.user, meta=user_meta)

    """
    uploads, files = [], []
    for uploaded_file in uploaded_files:
        files.append({k:uploaded_file[k] for k in uploaded_file if k in ['file_name', 'file_mime', 'file_path', 'file_size', 'file_error']})
        if not uploaded_file['file_error']:
            upload = insert(Upload, user_id=g.user.id, comment_id=comment.id, upload_name=uploaded_file['file_name'], upload_file=uploaded_file['file_path'], upload_mime=uploaded_file['file_mime'], upload_size=uploaded_file['file_size'])
            uploads.append({k:upload.__dict__[k] for k in upload.__dict__ if k in ['id', 'comment_id', 'created', 'upload_name', 'upload_file', 'upload_mime', 'upload_size']})
    """

    return {
        'uploads': 'uploads',
        'files': 'files',
    }, {}, 200