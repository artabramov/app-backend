from flask import g, request
from app import app, err, log
from app.core.app_response import app_response
from app.core.user_auth import user_auth
from app.core.basic_handlers import insert, update, delete, select, select_all
from app.models.user import User
from app.models.post import Post
from app.models.upload import Upload
from multiprocessing import Process, Manager
from app.core.upload_async import upload_async
from app.core.upload_files import upload_files
from app.core.file_delete import file_delete


def to_dict(upload):
    user = select(User, id=upload.user_id)
    post = select(Post, id=upload.post_id)
    return {
        'id': upload.id, 
        'created': upload.created, 
        'user_id': upload.user_id,
        'user': {'user_login': user.user_login},
        'post_id': upload.post_id,
        'post': {'post_title': post.post_title},
        'upload_name': upload.upload_name,
        'upload_link': upload.upload_link,
        'upload_mime': upload.upload_mime,
        'upload_size': upload.upload_size,
    }


@app.route('/uploads/', methods=['POST'], endpoint='uploads_insert')
@app_response
@user_auth
def uploads_insert():
    if not g.user.can_edit:
        return {}, {'user_token': [err.PERMISSION_DENIED], }, 200

    post_id = request.args.get('post_id')
    user_files = request.files.getlist('user_files')

    post = select(Post, id=post_id)
    if not post:
        return {}, {'post_id': [err.VALUE_NOT_FOUND], }, 200

    try:
        uploaded_files = upload_files(user_files)
    except Exception as e:
        log.error(e)

    uploads, errors = [], {}
    for uploaded_file in uploaded_files:
        if not uploaded_file['error']:
            upload = insert(
                Upload, 
                user_id=g.user.id, 
                post_id=post.id, 
                upload_name=uploaded_file['name'], 
                upload_path=uploaded_file['path'], 
                upload_link=uploaded_file['link'], 
                upload_mime=uploaded_file['mime'], 
                upload_size=uploaded_file['size'],
            )

            uploads.append({k:upload.__dict__[k] for k in upload.__dict__ if k in [
                'id', 
                'post_id', 
                'created', 
                'upload_name', 
                'upload_path', 
                'upload_link', 
                'upload_mime', 
                'upload_size',
            ]})
        
        else:
            errors[uploaded_file['name']] = [uploaded_file['error']]

    return {
        'uploads': uploads,
    }, errors, 201


@app.route('/upload/<int:upload_id>/', methods=['PUT'], endpoint='upload_update')
@app_response
@user_auth
def upload_update(upload_id):
    if not g.user.can_edit:
        return {}, {'user_token': [err.PERMISSION_DENIED], }, 200

    upload_name = request.args.get('upload_name')

    upload = select(Upload, id=upload_id)
    if not upload:
        return {}, {'upload_id': [err.VALUE_NOT_FOUND]}, 200
    
    upload = update(upload, upload_name=upload_name)
    return {}, {}, 200


@app.route('/upload/<int:upload_id>/', methods=['DELETE'], endpoint='upload_delete')
@app_response
@user_auth
def upload_delete(upload_id):
    if not g.user.can_admin:
        return {}, {'user_token': [err.PERMISSION_DENIED], }, 200

    upload = select(Upload, id=upload_id)
    if not upload:
        return {}, {'upload_id': [err.VALUE_NOT_FOUND]}, 200

    file_delete(upload.upload_path)
    delete(upload)
    return {}, {}, 200


@app.route('/uploads/<int:post_id>/', methods=['GET'], endpoint='uploads_list')
@app_response
@user_auth
def uploads_list(post_id):
    if not g.user.can_read:
        return {}, {'user_token': [err.PERMISSION_DENIED], }, 200

    uploads = select_all(Upload, post_id=post_id)
    return {
        'uploads': [to_dict(upload) for upload in uploads],
    }, {}, 200
