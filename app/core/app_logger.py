from logging.handlers import RotatingFileHandler
from flask import request, g, has_request_context
import logging
import json
import time
import uuid
import sys
import traceback

SENSITIVE_KEYS = ['user_token', 'user-token']
SENSITIVE_VALUE = '*' * 4


def obscure_data(result_dict, original_dict):
    for key, value in original_dict.items():
        if isinstance(value, dict):
            result_dict[key] = obscure_data(result_dict.get(key, {}), value)
        else:
            result_dict[key] = SENSITIVE_VALUE if key.casefold() in SENSITIVE_KEYS else value
    return result_dict


def create_logger(app):
    class ContextualFilter(logging.Filter):
        def filter(self, message):
            message.uuid = g.request_context.uuid
            message.tb = str(list(traceback.extract_stack()))
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
        request_dict = {
            'request': request.url,
            'method': request.method,
            'headers': obscure_data(dict(), dict(request.headers))}
        app.logger.debug(str(request_dict))        

    @app.after_request
    def after_request(response):
        try:
            response_dict = json.loads(response.data)
        except Exception as e:
            response_dict = {'response': str(response.data)}
        response_dict = obscure_data(dict(), response_dict)
        app.logger.debug({
            'response': str(response_dict),
            'duration': g.request_context.duration,
            })
        return response

    return app.logger


class RequestContext:
    def __init__(self, req):
        self.start_time = time.time()
        self.uuid = str(uuid.uuid4())

    @property
    def duration(self):
        return time.time() - self.start_time
