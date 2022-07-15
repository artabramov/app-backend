from app import app
from multiprocessing import Process, Manager
from app.core.upload_async import upload_async
from app.core.upload_sync import upload_sync
from app.core.basic_handlers import insert, update, delete, select, select_all


UPLOADS_ASYNC = app.config['UPLOADS_ASYNC']

def upload_files(user_files):
    if UPLOADS_ASYNC:
        manager = Manager()
        uploaded_files = manager.list() # do not rename variable "uploaded_files"

        jobs = []
        for user_file in user_files:
            job = Process(target=upload_async, args=(user_file, uploaded_files))
            jobs.append(job)
            job.start()
        
        for job in jobs:
            job.join()

    else:
        uploaded_files = upload_sync(user_files)

    return uploaded_files
