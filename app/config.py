import sys


class Config:
    #DEBUG = True

    LOG_LEVEL = 'DEBUG'
    LOG_FILENAME = '/var/log/app/app.log'
    LOG_FORMAT = '[%(asctime)s] %(levelname)s uuid: "%(uuid)s", %(name)s in %(filename)s line %(lineno)d: "%(message)s"'
    LOG_MAX_BYTES = 1024 * 10 # 10 KB
    LOG_BACKUP_COUNT = 5

    QR_PATH_MASK = '/app/qr/%s.png'
    QR_URI_MASK = 'http://localhost:8080/qr/%s.png'
    QR_LINK_MASK = 'otpauth://totp/myapp?secret=%s&issuer=%s'

    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://admin:admin@host.docker.internal:3306/app'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CELERY_BROKER_URI = 'redis://host.docker.internal:6379/0'
    CELERY_BACKEND_URI = 'redis://host.docker.internal:6379/1'
    CELERY_TASKS_LIST = ['app.user.user_tasks']
    CELERY_ROUTING_KEYS = {
        'app.user_insert': {'queue': 'celery'}
    }
    CELERY_RESULT_EXPIRES = 30

    UPLOAD_FOLDER = '/var'
    UPLOAD_IMAGES_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
    UPLOAD_DOCUMENTS_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
