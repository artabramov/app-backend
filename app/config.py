import sys


class Config:
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

    USER_IMAGES_PATH = '/app/images/'
    USER_IMAGES_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

    #UPLOAD_DOCUMENTS_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
