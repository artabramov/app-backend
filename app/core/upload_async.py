import os, uuid
from app import app, log
from datetime import date

UPLOADS_PATH = app.config['UPLOADS_PATH']
UPLOADS_LINK = app.config['UPLOADS_LINK']
UPLOADS_MIMES = app.config['UPLOADS_MIMES']


def upload_async(user_file, uploaded_files, allowed_mimes=[]):

    if not allowed_mimes:
        allowed_mimes=UPLOADS_MIMES

    file_data = {
        'name': user_file.filename,
        'mime': user_file.mimetype,
        'path': '',
        'link': '',
        'size': 0,
        'error': '',
    }

    if not user_file or not user_file.filename:
        file_data['error'] = 'File not found'
        uploaded_files.append(file_data)
        return

    if allowed_mimes and user_file.mimetype not in allowed_mimes:
        file_data['error'] = 'File mimetype is incorrect'
        uploaded_files.append(file_data)
        return

    try:
        dst_dir = '%s-%s-%s/' % (date.today().year, date.today().month, date.today().day)
        dst_path = os.path.join(UPLOADS_PATH, dst_dir)
        if not os.path.exists(dst_path):
                os.mkdir(dst_path)

        file_ext = user_file.filename.rsplit('.', 1)[1].lower()
        file_name = str(uuid.uuid4()) + '.' + file_ext
        file_path = os.path.join(dst_path, file_name)
        user_file.save(file_path)

    except IOError as e:
        log.error(e)
        file_data['error'] = 'File IO error'
        uploaded_files.append(file_data)
        return

    except Exception as e:
        log.error(e)
        file_data['error'] = str(e)
        uploaded_files.append(file_data)
        return

    file_data['path'] = file_path
    file_data['link'] = UPLOADS_LINK + dst_dir + file_name
    file_data['size'] = os.path.getsize(file_path)
    uploaded_files.append(file_data)
    return
