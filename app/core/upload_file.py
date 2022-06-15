import os, uuid
from app import app, log
from datetime import date

APP_DIR = app.config['APP_DIR']
APP_URL = app.config['APP_URL']
IMAGES_DIR = app.config['IMAGES_DIR']


def upload_file(user_file, upload_dir, allowed_mimes, uploaded_files):

    file_data = {
        'name': user_file.filename,
        'mime': user_file.mimetype,
        'file': '',
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
        if upload_dir != IMAGES_DIR:
            file_dir = '%s-%s-%s' % (date.today().year, date.today().month, date.today().day)
            upload_dir = os.path.join(upload_dir, file_dir)
            if not os.path.exists(upload_dir):
                os.mkdir(upload_dir)

        file_ext = user_file.filename.rsplit('.', 1)[1].lower()
        file_name = str(uuid.uuid4()) + '.' + file_ext
        
        upload_file = os.path.join(upload_dir, file_name)

        user_file.save(upload_file)
        file_data['file'] = os.path.join(file_dir, file_name)
        file_data['size'] = os.path.getsize(upload_file)

    except IOError as e:
        log.error(e)
        file_data['error'] = 'File IO error'

    except Exception as e:
        log.error(e)
        file_data['error'] = 'Internal server error'

    uploaded_files.append(file_data)
    return
