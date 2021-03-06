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

    APP_PATH = '/app/'
    APP_LINK = 'http://localhost/'

    UPLOADS_ASYNC = False
    UPLOADS_PATH = '/app/uploads/'
    UPLOADS_LINK = 'http://localhost/uploads/'
    UPLOADS_MIMES = ['image/jpeg']

    IMAGES_PATH = '/app/images/'
    IMAGES_LINK = 'http://localhost/images/'
    IMAGES_MIMES = ['image/jpeg']
    IMAGES_SIZE = (640, 480)
    IMAGES_QUALITY = 90

    QRCODES_PATH = '/app/qrcodes/'
    QRCODES_LINK = 'http://localhost/qrcodes/'
    QRCODES_REF = 'otpauth://totp/myapp?secret=%s&issuer=%s'
    QRCODES_SIZE = 8
    QRCODES_BORDER = 1
    QRCODES_COLOR = 'black'
    QRCODES_BACKGROUND = 'white'

    USER_PASS_HASH_SALT = 'abcd'
    USER_PASS_ATTEMPTS_LIMIT = 5
    USER_PASS_SUSPEND_TIME = 30
    USER_TOTP_ATTEMPTS_LIMIT = 5
    USER_TOKEN_EXPIRATION_TIME = 60 * 60 * 24 * 7
    USER_SELECT_LIMIT = 2

    VOLUME_SELECT_LIMIT = 2

    POST_SELECT_LIMIT = 2

    COMMENT_SELECT_LIMIT = 2



