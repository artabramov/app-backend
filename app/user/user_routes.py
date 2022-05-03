from flask import request, g
from app import app, log
from app.core.response import response
from app.user.user_tasks import user_register, user_restore, user_signin, user_signout, user_select, user_update
from celery.exceptions import TimeoutError

# user register
@app.route('/user/', methods=['POST'])
def user_post():
    user_login = request.args.get('user_login', '')
    user_name = request.args.get('user_name', '')
    user_pass = request.args.get('user_pass', '')

    try:
        async_result = user_register.apply_async(args=[
            user_login, user_name, user_pass
        ], task_id=g.request_context.uuid).get(timeout=10)
        return response(*async_result)

    except TimeoutError as e:
        log.error(e)
        return response({}, {'db': ['Gateway Timeout']}, 504)


# user restore
@app.route('/pass/', methods=['GET'])
def pass_get():
    try:
        user_login = request.args.get('user_login', '')
        user_pass = request.args.get('user_pass', '')
        async_result = user_restore.apply_async(args=[user_login, user_pass], task_id=g.request_context.uuid).get(timeout=10)
        return response(*async_result)

    except TimeoutError as e:
        log.error(e)
        return response({}, {'db': ['Gateway Timeout']}, 504)


# user signin
@app.route('/token/', methods=['GET'])
def token_get():
    try:
        user_login = request.args.get('user_login', '')
        user_code = request.args.get('user_code', '')
        async_result = user_signin.apply_async(args=[user_login, user_code], task_id=g.request_context.uuid).get(timeout=10)
        return response(*async_result)

    except TimeoutError as e:
        log.error(e)
        return response({}, {'db': ['Gateway Timeout']}, 504)


# user signout
@app.route('/token/', methods=['PUT'])
def token_put():
    try:
        user_token = request.headers.get('user_token')
        async_result = user_signout.apply_async(args=[user_token], task_id=g.request_context.uuid).get(timeout=10)
        return response(*async_result)

    except TimeoutError as e:
        log.error(e)
        return response({}, {'db': ['Gateway Timeout']}, 504)


# user select
@app.route('/user/<user_id>', methods=['GET'])
def user_get(user_id):
    try:
        user_token = request.headers.get('user_token')
        async_result = user_select.apply_async(args=[user_token, user_id], task_id=g.request_context.uuid).get(timeout=10)
        return response(*async_result)

    except TimeoutError as e:
        log.error(e)
        return response({}, {'db': ['Gateway Timeout']}, 504)


# user update
@app.route('/user/<user_id>', methods=['PUT'])
def user_put(user_id):
    try:
        user_id = int(user_id)
        user_token = request.headers.get('user_token', None)
        user_name = request.args.get('user_name', None)
        user_role = request.args.get('user_role', None)
        user_pass = request.args.get('user_pass', None)
        async_result = user_update.apply_async(args=[user_token, user_id, user_name, user_role, user_pass], task_id=g.request_context.uuid).get(timeout=10)
        #async_result = user_update(user_token, user_id, user_name, is_admin)
        return response(*async_result)

    except TimeoutError as e:
        log.error(e)
        return response({}, {'db': ['Gateway Timeout']}, 504)



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['UPLOAD_IMAGES_EXTENSIONS']


# user image upload
@app.route('/image/', methods=['POST'])
def image_post():
    from werkzeug.utils import secure_filename
    #from flask import url_for
    import os

    if 'file' not in request.files:
        return response({}, {'image': ['where is the file? 1']}, 504)

    file = request.files['file']
    if file.filename == '':
        return response({}, {'image': ['where is the file? 2']}, 504)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return response({}, {'file': str(file)}, 200)

    return response({}, {}, 200)

