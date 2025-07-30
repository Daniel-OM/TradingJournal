
from .app import create_app
from .config import ProdConfig

class PrefixMiddleware:
    def __init__(self, app, prefix):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        script_name = self.prefix
        if environ['PATH_INFO'].startswith(script_name):
            environ['SCRIPT_NAME'] = script_name
            environ['PATH_INFO'] = environ['PATH_INFO'][len(script_name):]
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            return [b"This URL does not belong to the app."]

# app = PrefixMiddleware(create_app(ProdConfig), prefix='/trading-journal')

from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = DispatcherMiddleware(None, {
	'/trading-journal': create_app(ProdConfig),
})

from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

if __name__ == "__main__":
    app.run(port=5002)
