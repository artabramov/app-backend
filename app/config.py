import sys


class Config:
    #DEBUG = True

    IS_CELERY = sys.argv and sys.argv[0].endswith('celery') and 'worker' in sys.argv

    LOG_LEVEL = 'DEBUG'
    LOG_FILENAME = '/var/log/app/app.log'
    if IS_CELERY:
        LOG_FORMAT = '{time: "%(asctime)s", level: "%(levelname)s", tag: "celery", filename: "%(filename)s", lineno: "%(lineno)d", message: "%(message)s"}'
    else:
        LOG_FORMAT = '{time: "%(asctime)s", level: "%(levelname)s", tag: "app", request: "%(request)s", method: "%(method)s", headers: "%(headers)s", message: "%(message)s"}'
    LOG_MAX_BYTES = 1024 * 10 # 10 KB
    LOG_BACKUP_COUNT = 5
    LOG_SENSITIVE_KEYS = ['user_token']
    LOG_SENSITIVE_VALUE = '*' * 4

    APP_LOG_LEVEL = 'DEBUG'
    APP_LOG_FILENAME = '/var/log/app/app.log'
    APP_LOG_FORMAT = '[%(asctime)s] %(levelname)s duration: "%(duration)s", request: "%(request)s", method: "%(method)s", headers: "%(headers)s", %(name)s in %(filename)s line %(lineno)d: "%(message)s"'
    APP_LOG_MAX_BYTES = 1024 * 10 # 10 KB
    APP_LOG_BACKUP_COUNT = 5
    APP_LOG_SENSITIVE_KEYS = ['user_token']
    APP_LOG_SENSITIVE_VALUE = '*' * 4

    CELERY_LOG_LEVEL = 'DEBUG'
    CELERY_LOG_FILENAME = '/var/log/celery/celery.log'
    CELERY_LOG_FORMAT = '[%(asctime)s] %(levelname)s %(name)s in %(filename)s line %(lineno)d: "%(message)s"'
    CELERY_LOG_MAX_BYTES = 1024 * 10 # 10 KB
    CELERY_LOG_BACKUP_COUNT = 5

    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://admin:admin@host.docker.internal:3306/owl'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CELERY_BROKER_URI = 'redis://host.docker.internal:6379/0'
    CELERY_BACKEND_URI = 'redis://host.docker.internal:6379/1'
    CELERY_TASKS_LIST = ['app.user.user_tasks']
    CELERY_ROUTING_KEYS = {
        'app.user_insert': {'queue': 'celery'}
    }
    CELERY_RESULT_EXPIRES = 30
