from flask import g, request
from app import app
from app.core.app_response import app_response
from app.core.user_auth import user_auth
from app.core.basic_handlers import insert, update, delete, select, select_all
from app.upload.upload_async import upload_async
from app.comment.comment import Comment
from app.upload.upload import Upload
from multiprocessing import Process, Manager
from app.upload.upload_files import upload_files

@app.route('/uploads/', methods=['POST'], endpoint='uploads_insert')
@app_response
@user_auth
def uploads_insert():
    """
    Uploads insert
    headers: user_token
    params: comment_id
    body: user_files
    """
    if not g.user.can_edit:
        return {}, {'user_token': ['user have not permissions for edit'], }, 406

    comment_id = request.args.get('comment_id')
    comment = select(Comment, id=comment_id, deleted=0)
    if not comment:
        return {}, {'comment_id': ['comment not found or deleted'], }, 404

    user_files = request.files.getlist('user_files')
    """
    manager = Manager()
    uploaded_files = manager.list() # do not rename variable "uploaded_files"

    jobs = []
    for user_file in user_files:
        job = Process(target=upload_async, args=(user_file, uploaded_files))
        jobs.append(job)
        job.start()
    
    for job in jobs:
        job.join()

    uploads, files = [], []
    for uploaded_file in uploaded_files:
        files.append({k:uploaded_file[k] for k in uploaded_file if k in ['name', 'mime', 'path', 'link', 'size', 'error']})
        if not uploaded_file['error']:
            upload = insert(Upload, user_id=g.user.id, comment_id=comment.id, upload_name=uploaded_file['name'], upload_path=uploaded_file['path'], upload_link=uploaded_file['link'], upload_mime=uploaded_file['mime'], upload_size=uploaded_file['size'])
            uploads.append({k:upload.__dict__[k] for k in upload.__dict__ if k in ['id', 'comment_id', 'created', 'upload_name', 'upload_path', 'upload_link', 'upload_mime', 'upload_size']})
    """

    uploaded_files = upload_files(user_files)
    files = []
    for uploaded_file in uploaded_files:
        files.append({k:uploaded_file[k] for k in uploaded_file if k in ['name', 'mime', 'path', 'link', 'size', 'error']})
        if not uploaded_file['error']:
            upload = insert(Upload, user_id=g.user.id, comment_id=comment.id, upload_name=uploaded_file['name'], upload_path=uploaded_file['path'], upload_link=uploaded_file['link'], upload_mime=uploaded_file['mime'], upload_size=uploaded_file['size'])

    return {
        'files': files,
    }, {}, 200


@app.route('/upload/<int:upload_id>', methods=['PUT'], endpoint='upload_update')
@app_response
@user_auth
def upload_update(upload_id):
    """ Upload update """
    if not g.user.can_edit:
        return {}, {'user_token': ['user_token must have edit permissions'], }, 406

    upload = select(Upload, id=upload_id, deleted=0)
    if not upload:
        return {}, {'upload_id': ['upload not found or deleted']}, 404

    upload_name = request.args.get('upload_name')
    if upload_name:
        upload = update(upload, upload_name=upload_name)

    return {}, {}, 200


@app.route('/upload/<int:upload_id>', methods=['DELETE'], endpoint='upload_delete')
@app_response
@user_auth
def upload_delete(upload_id):
    """ Upload delete """
    if not g.user.can_edit:
        return {}, {'user_token': ['user_token must have edit permissions'], }, 406

    upload = select(Upload, id=upload_id, deleted=0)
    if not upload:
        return {}, {'upload_id': ['upload not found']}, 404

    delete(upload)
    return {}, {}, 200
