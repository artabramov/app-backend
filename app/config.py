class Config:
    LOG_LEVEL = 'DEBUG'
    LOG_FILENAME = '/var/log/app/app.log'
    LOG_FORMAT = '[%(asctime)s] %(levelname)s uuid: "%(uuid)s", %(name)s in %(filename)s line %(lineno)d: "%(message)s", tb: "%(tb)s"'
    LOG_MAX_BYTES = 1024 * 1024 * 1 # 1 Mb
    LOG_BACKUP_COUNT = 5

    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:postgres@host.docker.internal:5432/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CACHE_TYPE = 'redis'
    CACHE_DEFAULT_TIMEOUT = 60 * 5
    CACHE_KEY_PREFIX = 'cache.'
    CACHE_REDIS_HOST = 'host.docker.internal'
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_PASSWORD = ''

    #APP_PATH = '/app/'
    #APP_LINK = 'http://localhost:8080/'

    UPLOADS_PATH = '/app/uploads/'
    UPLOADS_LINK = 'http://localhost:8080/uploads/'
    UPLOADS_MIMES = ['image/jpeg']

    IMAGES_PATH = '/app/images/'
    IMAGES_LINK = 'http://localhost:8080/images/'
    IMAGES_MIMES = ['image/jpeg']
    IMAGES_SIZE = (320, 240)
    IMAGES_QUALITY = 90

    QRCODES_PATH = '/app/qrcodes/'
    QRCODES_LINK = 'http://localhost:8080/qrcodes/'
    QRCODES_REF = 'otpauth://totp/myapp?secret=%s&issuer=%s'



    #UPLOAD_DOCUMENTS_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
