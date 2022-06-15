from flask import request
from app import app, log
from multiprocessing import Process
from multiprocessing import Manager
from app.core.app_response import app_response
from app.core.upload_file import upload_file
from app.user.user import PASS_ATTEMPTS_LIMIT, PASS_SUSPEND_TIME, TOTP_ATTEMPTS_LIMIT, TOKEN_EXPIRATION_TIME
from app.user.user import User
import time
import os

from app.core.basic_handlers import insert, update, delete, select, select_all
from app.core.user_auth import user_auth
from app.core.qrcode_handlers import qrcode_make, qrcode_remove
from flask import g
from PIL import Image

QRCODES_URL = app.config['QRCODES_URL']
IMAGES_DIR = app.config['IMAGES_DIR']
IMAGES_URL = app.config['IMAGES_URL']
IMAGES_MIMES = app.config['IMAGES_MIMES']
IMAGES_SIZE =  app.config['IMAGES_SIZE']
IMAGES_QUALITY =  app.config['IMAGES_QUALITY']


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
        'totp_qrcode': QRCODES_URL + user.totp_key + '.png'
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
    try:
        user_file = request.files.getlist('user_file')[0]
    except:
        return {}, {'user_file': ['user_file not found']}, 404
    
    manager = Manager()
    uploaded_files = manager.list() # do not rename this variable

    job = Process(target=upload_file, args=(user_file, IMAGES_DIR, IMAGES_URL, IMAGES_MIMES, uploaded_files))
    job.start()
    job.join()

    uploaded_file = uploaded_files[0]
    if uploaded_file['error']:
        return {}, {'user_file': [uploaded_file['error']]}, 404

    image_file = g.user.get_meta('image_file')
    if image_file and os.path.isfile(image_file):
        os.remove(image_file)

    image = Image.open(uploaded_file['file'])
    image.thumbnail(IMAGES_SIZE, Image.ANTIALIAS)
    image.save(uploaded_file['file'], quality=IMAGES_QUALITY)

    user_meta = {
        'image_file': uploaded_file['file'],
        'image_url': uploaded_file['url'],
    }
    update(g.user, meta=user_meta)
    return {
        'image_file': uploaded_file['file'],
        'image_url': uploaded_file['url'],
    }, {}, 200
