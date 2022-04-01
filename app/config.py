class Config:
    #DEBUG = True

    LOG_LEVEL = 'DEBUG'
    LOG_PATH = '/var/log/app/'
    LOG_FILENAME = 'app.log'
    LOG_FORMAT = '{time: "%(asctime)s", duration: "%(duration)s", level: "%(levelname)s", uuid: "%(uuid)s", url: "%(url)s", method: "%(method)s", headers: "%(headers)s", name: "%(name)s", filename: "%(filename)s", lineno: "%(lineno)d", message: "%(message)s"}'
    LOG_MAX_BYTES = 1024 * 1024 * 1 # 1 MB
    LOG_BACKUP_COUNT = 5
    LOG_SENSITIVE_KEYS = ['token']
    LOG_SENSITIVE_VALUE = '*' * 8

    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://admin:admin@host.docker.internal:3306/owl'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CELERY_BROKER_URL = 'redis://host.docker.internal:6379/0'
    CELERY_RESULT_BACKEND = 'redis://host.docker.internal:6379/1'
    CELERY_TASK_LIST = ['app.user']
    CELERY_RESULT_EXPIRES = 30
    CELERY_TASK_ROUTES = {
        'app.*': {'queue': 'user'}
    }