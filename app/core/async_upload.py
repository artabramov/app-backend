from marshmallow import ValidationError
import os
import uuid


def async_upload(user_file, file_path, allowed_mimes, uploaded_files):

    file_data = {
        'file': {
            'file_name': user_file.filename,
            'file_path': '',
            'file_size': '',
            'file_mime': ''
        },
        'error': ''
    }

    if not user_file or not user_file.filename:
        #raise IOError({'user_file': ['File not found']})
        #return {'file': {}, 'error': 'File not found'}
        #return_dict[file_name] = {'file': {}, 'error': 'File not found'}
        uploaded_files.append({'file': {'file_name': user_file.filename}, 'error': 'File not found'})
        return

    if allowed_mimes and user_file.mimetype not in allowed_mimes:
        #raise IOError({'user_file': ['File mimetype is incorrect']})
        #return {'file': {}, 'error': 'File mimetype is incorrect'}
        #return_dict[file_name] = {'file': {}, 'error': 'File mimetype is incorrect'}
        file_data['error'] = 'File mimetype is incorrect'
        uploaded_files.append(file_data)
        return

    file_ext = user_file.filename.rsplit('.', 1)[1].lower()
    file_name = os.path.join(file_path, str(uuid.uuid4()) + '.' + file_ext)

    try:
        user_file.save(file_name)
    except IOError:
        # TODO: add logging here
        #return {'file': {}, 'error': 'No such file or directory'}
        #return_dict[file_name] = {'file': {}, 'error': 'No such file or directory'}
        pass

    file_data = {
        'file': {
            'file_name': user_file.filename,
            'file_path': file_name,
            'file_size': os.path.getsize(file_name),
            'file_mime': user_file.mimetype,
        },
        'error': ''
    }

    #return file_data
    #return_dict[file_name] = file_data
    uploaded_files.append(file_data)



def old_file_upload(file, upload_path, allowed_exts=None):
    filename_src = getattr(file, 'filename', None)
    if not file or not filename_src:
        raise ValidationError({'file': ['Where is the file?']})

    file_ext = file.filename.rsplit('.', 1)[1].lower()
    if allowed_exts and file_ext not in allowed_exts:
        raise ValidationError({'file': ['Extension is incorrect']})

    filename_dst = os.path.join(upload_path, str(uuid.uuid4()) + '.' + file_ext)
    file.save(filename_dst)
    file_data = {
        'filename_src': filename_src,
        'filename_dst': filename_dst,
        'file_size': os.path.getsize(filename_dst),
        'file_mime': file.mimetype,
        'file_ext': file_ext,
    }
    return file_data
