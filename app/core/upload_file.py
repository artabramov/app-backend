from marshmallow import ValidationError
import os
import uuid


# TODO: make secure filename for DB!
def upload_file(user_file, file_path, allowed_mimes, uploaded_files):

    file_data = {
        'file_name': user_file.filename,
        'file_mime': user_file.mimetype,
        'file_path': '',
        'file_size': '',
        'file_error': '',
    }

    if not user_file or not user_file.filename:
        #raise IOError({'user_file': ['File not found']})
        #return {'file': {}, 'error': 'File not found'}
        #return_dict[file_name] = {'file': {}, 'error': 'File not found'}
        #uploaded_files.append({'file': {'file_name': user_file.filename}, 'error': 'File not found'})
        file_data['file_error'] = 'File not found'
        uploaded_files.append(file_data)
        return

    if allowed_mimes and user_file.mimetype not in allowed_mimes:
        #raise IOError({'user_file': ['File mimetype is incorrect']})
        #return {'file': {}, 'error': 'File mimetype is incorrect'}
        #return_dict[file_name] = {'file': {}, 'error': 'File mimetype is incorrect'}
        #uploaded_files.append(file_data)
        file_data['file_error'] = 'File mimetype is incorrect'
        uploaded_files.append(file_data)
        return

    file_ext = user_file.filename.rsplit('.', 1)[1].lower()
    file_name = os.path.join(file_path, str(uuid.uuid4()) + '.' + file_ext)

    try:
        user_file.save(file_name)
    except IOError:
        # TODO: ADD LOGGING!
        #return {'file': {}, 'error': 'No such file or directory'}
        #return_dict[file_name] = {'file': {}, 'error': 'No such file or directory'}
        pass

    file_data['file_path'] = file_name
    file_data['file_size'] = os.path.getsize(file_name)
    uploaded_files.append(file_data)
