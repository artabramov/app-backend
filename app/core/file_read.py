from marshmallow import ValidationError
import os
import uuid


def file_read(file):
    file_name = getattr(file, 'filename', None)
    file_ext = file.filename.rsplit('.', 1)[1].lower()
    file_bytes = file.read()
    #with open(file, 'rb') as f:
    #    file_bytes = f.read()

    file_data = {
        'file_name': file_name,
        'file_size': os.path.getsize(file_name),
        'file_mime': file.mimetype,
        'file_ext': file_ext,
        'file_bytes': file_bytes,
    }
    return file_data
