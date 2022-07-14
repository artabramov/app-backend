from flask import make_response, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from app import db, log, err


def app_response(func):
    def inner(*args, **kwargs):
        data, errors = {}, {}
        http_code = 200

        try:
            data, errors, http_code = func(*args, **kwargs)
            db.session.commit()

        except ValidationError as e:
            log.debug(e.messages)
            db.session.rollback()
            errors, http_code = e.messages, 200

        except SQLAlchemyError as e:
            log.error(e)
            db.session.rollback()
            errors, http_code = {'db': [err.SERVICE_UNAVAILABLE]}, 503

        except IOError as e:
            log.error(e)
            db.session.rollback()
            result = {}, {'error': [err.FILE_ERROR]}, 400

        except Exception as e:
            log.error(e)
            db.session.rollback()
            #errors, http_code = {'app': [err.SERVER_ERROR]}, 500
            errors, http_code = {'app': [str(e)]}, 500

        response = make_response(
            jsonify({
                'data': data,
                'errors': errors,
            }), http_code)
        response.headers['Content-Type'] = 'application/json'
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    return inner
