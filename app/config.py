class Config:
    DEBUG = True

    LOG_FILENAME = '/var/log/app/app.log'
    LOG_FORMAT = '[%(asctime)s] level: "%(levelname)s", uuid: "%(uuid)s", duration: "%(duration)s", url: "%(url)s", method: "%(method)s", headers: "%(headers)s", [%(name)s in %(filename)s, line %(lineno)d: "%(message)s"]'
    LOG_ROTATE_WHEN = 'H'
    LOG_BACKUP_COUNT = 24

    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://admin:admin@host.docker.internal:3306/echidna'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CELERY_BROKER_URL = 'amqp://guest:guest@host.docker.internal:5672//'
    CELERY_RESULT_BACKEND = 'redis://host.docker.internal:6379/0'
    CELERY_TASK_LIST = ['app.tasks']
    CELERY_RESULT_EXPIRES = 30
    CELERY_TASK_ROUTES = {
        'app.*': {'queue': 'user'}
    }