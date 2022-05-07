from marshmallow import ValidationError
import os
import uuid


def file_upload(file, upload_path, allowed_exts=None):
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
