from flask import make_response, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from app import db, log


def make_json(data={}, errors={}, code=200):
    response = make_response(
        jsonify({
            'data': data,
            'errors': errors,
        }), code)
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


def json_response(func):
    def inner(*args):
        try:
            result = func(*args)
            
        except ValidationError as e:
            log.debug(e.messages)
            db.session.rollback()
            result = {}, e.messages, 400

        except SQLAlchemyError as e:
            log.error(e)
            db.session.rollback()
            result = {}, {'error': ['Service Unavailable']}, 503

        except Exception as e:
            #import sys, os
            #exc_type, exc_obj, exc_tb = sys.exc_info()
            #fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            
            #log.error(e, exc_info=(exc_type, exc_value, exc_traceback))
            
            log.error(e)
            db.session.rollback()
            result = {}, {'error': ['Internal Server Error']}, 500

        return make_json(*result)
    return inner
