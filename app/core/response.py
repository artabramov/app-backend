from flask import make_response, jsonify

def response(data={}, errors={}, code=200):
    response = make_response(
        jsonify(
            {
                'data': data,
                'errors': errors,
                'user_token': 'askldfhaskdhfaskfd',
            }
        ),
        code,
    )
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Server'] = 'noserver!'
    return response