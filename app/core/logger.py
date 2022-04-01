from flask import request, g
from time import time
from logging.handlers import RotatingFileHandler
import logging
import json
#import os, pwd, grp


def obscure_data(result_dict, original_dict, sensitive_keys, sensitive_value):
    for key, value in original_dict.items():
        if isinstance(value, dict):
            result_dict[key] = obscure_data(result_dict.get(key, {}), value, sensitive_keys, sensitive_value)
        else:
            result_dict[key] = sensitive_value if key.casefold() in sensitive_keys else value
    return result_dict


def create_logger(app):
    #log_file = app.config['LOG_PATH'] + app.config['LOG_FILENAME']



    #for file in os.listdir(app.config['LOG_PATH']):
    #    uid = pwd.getpwnam('www-data').pw_uid
    #    gid = grp.getgrnam('www-data').gr_gid
    #    os.chown(app.config['LOG_PATH'] + file, uid, gid)
    
    class ContextualFilter(logging.Filter):
        def filter(self, message):
            if not app.config['IS_CELERY']:
                message.request = request.url
                message.method = request.method
                message.headers = str(dict(request.headers))
                message.duration = g.request_context.duration
            return True

    while app.logger.hasHandlers():
        app.logger.removeHandler(app.logger.handlers[0])

    handler = RotatingFileHandler(
        filename=app.config['LOG_FILENAME'], 
        maxBytes=app.config['LOG_MAX_BYTES'], 
        backupCount=app.config['LOG_BACKUP_COUNT'])
    handler.setFormatter(logging.Formatter(app.config['LOG_FORMAT']))

    app.logger.addHandler(handler)
    app.logger.addFilter(ContextualFilter())

    level = logging.getLevelName(app.config['LOG_LEVEL'])
    app.logger.setLevel(level)
        
    @app.before_request
    def before_request():
        g.request_context = RequestContext(request)

    @app.after_request
    def after_request(response):
        response_dict = json.loads(response.data)
        response_dict = obscure_data(dict(), response_dict, app.config['LOG_SENSITIVE_KEYS'], app.config['LOG_SENSITIVE_VALUE'])
        app.logger.debug(str(response_dict))
        return response

    return app.logger


class RequestContext:
    def __init__(self, req):
        self.start_time = time()

    @property
    def duration(self):
        return time() - self.start_time
