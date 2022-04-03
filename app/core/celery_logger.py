from logging.handlers import RotatingFileHandler
import logging
from ..config import Config

CELERY_LOG_LEVEL = Config.CELERY_LOG_LEVEL
CELERY_LOG_FILENAME = Config.CELERY_LOG_FILENAME
CELERY_LOG_FORMAT = Config.CELERY_LOG_FORMAT
CELERY_LOG_MAX_BYTES = Config.CELERY_LOG_MAX_BYTES
CELERY_LOG_BACKUP_COUNT = Config.CELERY_LOG_BACKUP_COUNT


def create_celery_logger(name):
    logger = logging.getLogger(name)
    
    level = logging.getLevelName(CELERY_LOG_LEVEL)
    logger.setLevel(level)

    handler = RotatingFileHandler(
        filename=CELERY_LOG_FILENAME, 
        maxBytes=CELERY_LOG_MAX_BYTES, 
        backupCount=CELERY_LOG_BACKUP_COUNT)
    handler.setFormatter(logging.Formatter(CELERY_LOG_FORMAT))
    logger.addHandler(handler)

    return logger
