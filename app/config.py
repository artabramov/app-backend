import sys


class Config:
    #DEBUG = True

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

    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://admin:admin@host.docker.internal:3306/app'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CELERY_BROKER_URI = 'redis://host.docker.internal:6379/0'
    CELERY_BACKEND_URI = 'redis://host.docker.internal:6379/1'
    CELERY_TASKS_LIST = ['app.user.user_tasks']
    CELERY_ROUTING_KEYS = {
        'app.user_insert': {'queue': 'celery'}
    }
    CELERY_RESULT_EXPIRES = 30
