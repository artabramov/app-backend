import os, uuid
from app import app, log
from datetime import date

IMAGES_PATH = app.config['IMAGES_PATH']


def upload_file(user_file, upload_path, allowed_mimes, uploaded_files):

    file_data = {
        'file_name': user_file.filename,
        'file_mime': user_file.mimetype,
        'file_path': '',
        'file_size': 0,
        'file_error': '',
    }

    if not user_file or not user_file.filename:
        file_data['file_error'] = 'File not found'
        uploaded_files.append(file_data)
        return

    if allowed_mimes and user_file.mimetype not in allowed_mimes:
        file_data['file_error'] = 'File mimetype is incorrect'
        uploaded_files.append(file_data)
        return

    try:
        if upload_path == IMAGES_PATH:
            file_path = upload_path

        else:
            file_path = os.path.join(upload_path, '%s-%s-%s' % (date.today().year, date.today().month, date.today().day))
            if not os.path.exists(file_path):
                os.mkdir(file_path)

        file_ext = user_file.filename.rsplit('.', 1)[1].lower()
        file_name = os.path.join(file_path, str(uuid.uuid4()) + '.' + file_ext)

        user_file.save(file_name)
        file_data['file_path'] = file_name
        file_data['file_size'] = os.path.getsize(file_name)

    except IOError as e:
        log.error(e)
        file_data['file_error'] = 'File IO error'

    except Exception as e:
        log.error(e)
        file_data['file_error'] = 'Internal server error'

    uploaded_files.append(file_data)
    return
