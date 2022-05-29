from flask import make_response, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from app import db, log


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
            errors, http_code = e.messages, 400

        except SQLAlchemyError as e:
            log.error(e)
            db.session.rollback()
            errors, http_code = {'db': ['Service Unavailable']}, 503

        #except IOError as e:
        #    log.error(e)
        #    result = {}, {'error': ['No such file or directory']}, 404

        except Exception as e:
            log.error(e)
            db.session.rollback()
            errors, http_code = {'app': ['Internal Server Error']}, 500

        response = make_response(
            jsonify({
                'data': data,
                'errors': errors,
            }), http_code)
        response.headers['Content-Type'] = 'application/json'
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    return inner
