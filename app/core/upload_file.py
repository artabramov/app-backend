import os, uuid
from app import app, log
from datetime import date

IMAGES_BASE_DIR = app.config['APP_BASE_DIR'] + app.config['IMAGES_DIR']


def upload_file(user_file, base_dir, base_url, allowed_mimes, uploaded_files):

    file_data = {
        'name': user_file.filename,
        'mime': user_file.mimetype,
        'file': '',
        'url': '',
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
        if base_dir != IMAGES_BASE_DIR:
            subdir = '%s-%s-%s' % (date.today().year, date.today().month, date.today().day)
            base_dir = os.path.join(base_dir, subdir)
            base_url = base_url + subdir + '/'
            if not os.path.exists(base_dir):
                os.mkdir(base_dir)

        file_ext = user_file.filename.rsplit('.', 1)[1].lower()
        file_name = str(uuid.uuid4()) + '.' + file_ext
        
        upload_file = os.path.join(base_dir, file_name)
        upload_url = os.path.join(base_url, file_name)

        user_file.save(upload_file)
        file_data['file'] = upload_file
        file_data['url'] = upload_url
        file_data['size'] = os.path.getsize(upload_file)

    except IOError as e:
        log.error(e)
        file_data['error'] = 'File IO error'

    except Exception as e:
        log.error(e)
        file_data['error'] = 'Internal server error'

    uploaded_files.append(file_data)
    return
