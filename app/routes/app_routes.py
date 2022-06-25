from app import app


@app.route('/', methods=['GET'], endpoint='app_route')
def app_route():
    return 'Hello, world!'
