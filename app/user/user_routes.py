import time, os, uuid
from flask import request, g
from PIL import Image
from app import app
from app.core.app_response import app_response
from app.core.basic_handlers import insert, update, delete, select, select_all, select_count
from app.core.user_auth import user_auth
from app.core.qrcode_handlers import qrcode_make, qrcode_remove
from app.user.user import User, UserRole

USER_PASS_ATTEMPTS_LIMIT = app.config['USER_PASS_ATTEMPTS_LIMIT']
USER_PASS_SUSPEND_TIME = app.config['USER_PASS_SUSPEND_TIME']
USER_TOTP_ATTEMPTS_LIMIT = app.config['USER_TOTP_ATTEMPTS_LIMIT']
USER_TOKEN_EXPIRATION_TIME = app.config['USER_TOKEN_EXPIRATION_TIME']
USER_SELECT_LIMIT = app.config['USER_SELECT_LIMIT']

QRCODES_LINK = app.config['QRCODES_LINK']

IMAGES_PATH = app.config['IMAGES_PATH']
IMAGES_LINK = app.config['IMAGES_LINK']
IMAGES_MIMES = app.config['IMAGES_MIMES']
IMAGES_SIZE =  app.config['IMAGES_SIZE']
IMAGES_QUALITY =  app.config['IMAGES_QUALITY']


@app.route('/user/', methods=['POST'], endpoint='user_register')
@app_response
def user_register():
    user_login = request.args.get('user_login', '').lower()
    user_name = request.args.get('user_name', '')
    user_pass = request.args.get('user_pass', '')

    user = insert(User, user_login=user_login, user_name=user_name, user_pass=user_pass)
    qrcode_make(user.totp_key, user.user_login)

    return {
        'totp_key': user.totp_key, 
        'totp_qrcode': QRCODES_LINK + user.totp_key + '.png'
    }, {}, 201


@app.route('/token/', methods=['GET'], endpoint='user_signin')
@app_response
def user_signin():
    user_login = request.args.get('user_login', '').lower()
    user_totp = request.args.get('user_totp', '')

    user = select(User, user_login=user_login, deleted=0)
    if not user:
        return {}, {'user_login': ['user not found or deleted'], }, 404

    elif user.totp_attempts >= USER_TOTP_ATTEMPTS_LIMIT:
        return {}, {'user_totp': ['user_totp attempts are over'], }, 406

    elif user_totp == user.user_totp:
        qrcode_remove(user.totp_key)
        token_expires = time.time() + USER_TOKEN_EXPIRATION_TIME
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
        if pass_attempts >= USER_PASS_ATTEMPTS_LIMIT:
            pass_attempts = 0
            pass_suspended = time.time() + USER_PASS_SUSPEND_TIME

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
            'created': user.created,
            'user_role': user.user_role.name,
            'user_name': user.user_name,
            'meta': {meta.meta_key: meta.meta_value for meta in user.meta if meta.meta_key in ['image_link']} 
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

    if not user_file or not user_file.filename:
        return {}, {'user_file': ['user_file not found'], }, 404

    if user_file.mimetype not in IMAGES_MIMES:
        return {}, {'user_file': ['File mimetype is incorrect'], }, 404

    file_ext = user_file.filename.rsplit('.', 1)[1].lower()
    file_name = str(uuid.uuid4()) + '.' + file_ext
    file_path = os.path.join(IMAGES_PATH, file_name)
    file_link = IMAGES_LINK + file_name
    user_file.save(file_path)

    image_path = g.user.get_meta('image_path')
    if image_path and os.path.isfile(image_path):
        os.remove(image_path)

    image = Image.open(file_path)
    image.thumbnail(IMAGES_SIZE, Image.ANTIALIAS)
    image.save(file_path, quality=IMAGES_QUALITY)

    user_meta = {
        'image_path': file_path,
        'image_link': file_link,
    }
    update(g.user, meta=user_meta)

    return {
        'image_link': file_link,
    }, {}, 200    


@app.route('/users/<int:offset>', methods=['GET'], endpoint='users_list')
@app_response
@user_auth
def users_list(offset):
    """ Users list """
    if not g.user.can_read:
        return {}, {'user_token': ['user_token must have read permissions'], }, 406

    users = select_all(User, deleted=0, offset=offset, limit=USER_SELECT_LIMIT)
    users_count = select_count(User, deleted=0)

    return {
        'users': [{
            'id': user.id,
            'created': user.created,
            'user_role': user.user_role.name,
            'user_name': user.user_name,
            'meta': {
                meta.meta_key: meta.meta_value for meta in user.meta if meta.meta_key in ['image_link']} 
        } for user in users],
        'users_count': users_count,
    }, {}, 200
