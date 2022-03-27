from flask import request, g
from uuid import uuid4
from time import time
#from logging.handlers import TimedRotatingFileHandler
from logging.handlers import RotatingFileHandler
import logging
import json
import os


def obscure_data(result_dict, original_dict, sensitive_keys, sensitive_value):
    for key, value in original_dict.items():
        if isinstance(value, dict):
            result_dict[key] = obscure_data(result_dict.get(key, {}), value, sensitive_keys, sensitive_value)
        else:
            result_dict[key] = sensitive_value if key.casefold() in sensitive_keys else value
    return result_dict


def create_logger(app):
    os.chmod(app.config['LOG_PATH'], 0o777)
    
    class ContextualFilter(logging.Filter):
        def filter(self, message):
            message.uuid = g.request_context.uuid
            message.url = g.request_context.url
            message.method = g.request_context.method
            message.headers = g.request_context.headers
            message.duration = g.request_context.duration
            return True

    while app.logger.hasHandlers():
        app.logger.removeHandler(app.logger.handlers[0])

    handler = RotatingFileHandler(
        filename=app.config['LOG_PATH'] + app.config['LOG_FILENAME'], 
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
        self.headers = str(dict(req.headers))
        self.url = req.url
        self.method = req.method
        self.start_time = time()
        self.uuid = str(uuid4())

    @property
    def duration(self):
        return time() - self.start_time
