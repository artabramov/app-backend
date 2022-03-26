from flask import request, g, has_request_context
import logging
from logging.handlers import TimedRotatingFileHandler
from uuid import uuid4
from time import time


def create_logger(app):

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

    handler = logging.handlers.TimedRotatingFileHandler(
        filename=app.config['LOG_FILENAME'], 
        when=app.config['LOG_ROTATE_WHEN'], 
        backupCount=app.config['LOG_BACKUP_COUNT'])
    handler.setFormatter(logging.Formatter(app.config['LOG_FORMAT']))

    app.logger.addHandler(handler)
    app.logger.addFilter(ContextualFilter())
    
    @app.before_request
    def before_request():
        g.request_context = RequestContext(request)


    @app.after_request
    def after_request(response):
        app.logger.debug('debug')
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
