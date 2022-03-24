class Config:
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://admin:admin@host.docker.internal:3306/echidna'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CELERY_BROKER_URL = 'amqp://guest:guest@host.docker.internal:5672//'
    CELERY_RESULT_BACKEND = 'redis://host.docker.internal:6379/0'
    CELERY_TASK_LIST = ['app.tasks']
    CELERY_RESULT_EXPIRES = 30
    CELERY_TASK_ROUTES = {
        'app.*': {'queue': 'user'}
    }