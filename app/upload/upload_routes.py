from flask import g, request
from app import app
from app.core.app_response import app_response
from app.core.user_auth import user_auth
from app.core.basic_handlers import insert, update, delete, select, search
from app.core.upload_file import upload_file
from app.comment.comment import Comment
from app.upload.upload import Upload
from multiprocessing import Process, Manager

UPLOAD_PATH = '/app/uploads/'
UPLOAD_MIMES = ['image/jpeg']


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
    manager = Manager()
    uploaded_files = manager.list() # do not rename variable "uploaded_files"

    jobs = []
    for user_file in user_files:
        job = Process(target=upload_file, args=(user_file, UPLOAD_PATH, UPLOAD_MIMES, uploaded_files))
        jobs.append(job)
        job.start()
    
    for job in jobs:
        job.join()

    uploads, files = [], []
    for uploaded_file in uploaded_files:
        files.append({k:uploaded_file[k] for k in uploaded_file if k in ['file_name', 'file_mime', 'file_path', 'file_size', 'file_error']})
        if not uploaded_file['file_error']:
            upload = insert(Upload, user_id=g.user.id, comment_id=comment.id, upload_name=uploaded_file['file_name'], upload_file=uploaded_file['file_path'], upload_mime=uploaded_file['file_mime'], upload_size=uploaded_file['file_size'])
            uploads.append({k:upload.__dict__[k] for k in upload.__dict__ if k in ['id', 'comment_id', 'created', 'upload_name', 'upload_file', 'upload_mime', 'upload_size']})

    return {
        'uploads': uploads,
        'files': files,
    }, {}, 200
