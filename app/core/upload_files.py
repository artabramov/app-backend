from multiprocessing import Process, Manager
from app.core.upload_async import upload_async
from app.core.basic_handlers import insert, update, delete, select, select_all


def upload_files(user_files):
    manager = Manager()
    uploaded_files = manager.list() # do not rename variable "uploaded_files"

    jobs = []
    for user_file in user_files:
        job = Process(target=upload_async, args=(user_file, uploaded_files))
        jobs.append(job)
        job.start()
    
    for job in jobs:
        job.join()

    return uploaded_files