from connexion import FlaskApp


class ConnexionApp(FlaskApp):
    def creare_api(self, specification, api_name, **kwargs):
        api = super(FlaskApp, self).add_api(specification, **kwargs)
        #app = self.app
        #self.app.register_blueprint(api.blueprint)

        @self.app.before_request
        def before_request():
            print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')

        @api.blueprint.after_request
        def after_request(response):
            a = 1
            print(a)
            return response

        return api
