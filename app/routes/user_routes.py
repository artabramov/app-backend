import time, os, uuid
from flask import request, g
from PIL import Image
from app import app, err
from app.core.app_response import app_response
from app.core.basic_handlers import insert, update, delete, select, select_all, select_count
from app.core.user_auth import user_auth
from app.core.qrcode_handlers import qrcode_make, qrcode_remove
from app.models.user import User, UserSchema

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


def to_dict(user):
    return  {
        'id': user.id,
        'created': user.created,
        'user_status': user.user_status.name,
        'user_login': user.user_login,
        'user_summary': user.user_summary if user.user_summary else '',
        'user_image': os.path.join(IMAGES_LINK, user.user_image) if user.user_image else '',
        'meta': {
            meta.meta_key: meta.meta_value for meta in user.meta if meta.meta_key in []
        } 
    }


@app.route('/user/', methods=['POST'], endpoint='user_register')
@app_response
def user_register():
    user_login = request.args.get('user_login', '').lower()
    user_pass = request.args.get('user_pass', '')

    user = insert(User, user_login=user_login, user_pass=user_pass)
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

    user = select(User, user_login=user_login)
    if not user:
        return {}, {'user_login': [err.VALUE_NOT_FOUND], }, 200

    elif user.user_status.name == 'blank':
        return {}, {'user_login': [err.PERMISSION_DENIED], }, 200

    elif user.totp_attempts >= USER_TOTP_ATTEMPTS_LIMIT:
        return {}, {'user_totp': [err.ATTEMPTS_ARE_OVER], }, 200

    elif user_totp == user.user_totp:
        qrcode_remove(user.totp_key)
        token_expires = time.time() + USER_TOKEN_EXPIRATION_TIME
        update(user, totp_attempts=0, token_expires=token_expires)
        return {'user_token': user.user_token}, {}, 200

    else:
        totp_attempts = user.totp_attempts + 1
        update(user, totp_attempts=totp_attempts)
        return {}, {'user_totp': [err.INVALID_VALUE], }, 200


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

    user = select(User, user_login=user_login)
    if not user:
        return {}, {'user_login': [err.VALUE_NOT_FOUND], }, 200

    elif user.user_status.name == 'blank':
        return {}, {'user_login': [err.PERMISSION_DENIED], }, 200

    elif user.pass_suspended > time.time():
        return {}, {'user_pass': [err.PERMISSION_SUSPENDED], }, 200

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
        return {}, {'user_pass': [err.INVALID_VALUE], }, 200


@app.route('/user/<int:user_id>/', methods=['GET'], endpoint='user_select')
@app_response
@user_auth
def user_select(user_id):
    user = select(User, id=user_id)

    if user:
        return {'user': to_dict(user)}, {}, 200

    else:
        return {}, {'user_id': [err.VALUE_NOT_FOUND]}, 200


@app.route('/user/<int:user_id>/', methods=['PUT'], endpoint='user_update')
@app_response
@user_auth
def user_update(user_id):
    if not g.user.can_read:
        return {}, {'user_token': [err.PERMISSION_DENIED], }, 200

    user = select(User, id=user_id)
    if not user:
        return {}, {'user_id': [err.VALUE_NOT_FOUND]}, 200

    elif user.id != g.user.id and not g.user.can_admin:
        return {}, {'user_token': [err.PERMISSION_DENIED], }, 200

    user_status = request.args.get('user_status', '')
    user_summary = request.args.get('user_summary', '')

    user_data = {}
    
    if user_status:
        if not g.user.can_admin or g.user.id == user.id:
            return {}, {'user_token': [err.PERMISSION_DENIED], }, 200

        else:
            user_data['user_status'] = user_status

    user_data['user_summary'] = user_summary

    update(user, **user_data, meta={})
    return {}, {}, 200


@app.route('/pass/', methods=['PUT'], endpoint='user_repass')
@app_response
@user_auth
def user_repass():
    if not g.user.can_read:
        return {}, {'user_token': [err.PERMISSION_DENIED], }, 200

    user_pass = request.args.get('user_pass', '')
    user_repass = request.args.get('user_repass', '')

    if g.user.pass_hash != User.get_pass_hash(g.user.user_login + user_pass):
        return {}, {'user_pass': [err.INVALID_VALUE], }, 200

    elif g.user.pass_hash == User.get_pass_hash(g.user.user_login + user_repass):
        return {}, {'user_repass': [err.INVALID_VALUE], }, 200

    try:
        UserSchema().load({'user_pass': user_repass})
    except:
        return {}, {'user_repass': [err.INVALID_VALUE], }, 200

    update(g.user, user_pass=user_repass)
    return {}, {}, 200


@app.route('/image/', methods=['POST'], endpoint='user_image')
@app_response
@user_auth
def user_image():
    if not g.user.can_read:
        return {}, {'user_token': [err.PERMISSION_DENIED], }, 200

    if g.user.user_image:
        user_image = os.path.join(IMAGES_PATH, g.user.user_image)
        if os.path.isfile(user_image):
            os.remove(user_image)

    try:
        user_file = request.files.getlist('user_file')[0]
    except:
        return {}, {'user_file': [err.VALUE_NOT_FOUND]}, 200

    if not user_file or not user_file.filename:
        return {}, {'user_file': [err.VALUE_NOT_FOUND], }, 200

    if user_file.mimetype not in IMAGES_MIMES:
        return {}, {'user_file': [err.INVALID_VALUE], }, 200

    file_ext = user_file.filename.rsplit('.', 1)[1].lower()
    file_name = str(uuid.uuid4()) + '.' + file_ext
    #file_path = os.path.join(IMAGES_PATH, file_name)
    #file_link = IMAGES_LINK + file_name
    user_image = os.path.join(IMAGES_PATH, file_name)
    user_file.save(user_image)

    image = Image.open(user_image)
    image.thumbnail(IMAGES_SIZE, Image.ANTIALIAS)
    image.save(user_image, quality=IMAGES_QUALITY)

    g.user.user_image = file_name
    update(g.user, meta={})

    return {
        'user_image': os.path.join(IMAGES_LINK, file_name),
    }, {}, 201


@app.route('/users/<int:offset>/', methods=['GET'], endpoint='users_list')
@app_response
@user_auth
def users_list(offset):
    if not g.user.can_read:
        return {}, {'user_token': [err.PERMISSION_DENIED], }, 200

    users = select_all(User, offset=offset, limit=USER_SELECT_LIMIT)
    users_count = select_count(User)

    return {
        'users': [to_dict(user) for user in users],
        'users_count': users_count,
    }, {}, 200
