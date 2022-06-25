from app import app
from flask import send_from_directory, url_for, render_template
import os


@app.route('/', methods=['GET'], endpoint='app_route')
def app_route():
    #return render_template('/app/app/static/index.html')
    content = open('/app/static/index.html').read()
    return app.send_static_file('/app/static/index.html')
    #tmp = url_for('static', filename='index.html')
    #return send_from_directory('static', 'index.html')


    #root_dir = os.path.dirname(os.getcwd())
    #return send_from_directory(os.path.join(root_dir, 'static'), 'index.html')

    #return 'Hello, world!'
    #return app.send_static_file('index.html')

    #return send_from_directory('/app/static/index.html')

    #return send_from_directory("static", "index.html")
    #return app.send_static_file('index.html') 
