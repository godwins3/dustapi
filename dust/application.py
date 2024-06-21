from werkzeug.wrappers import Request
from .routing import Router
from .responses import Response

class Application:
    def __init__(self):
        self.router = Router()

    def route(self, path, methods=["GET"]):
        def wrapper(handler):
            self.router.add_route(path, handler, methods)
            return handler
        return wrapper

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.router.dispatch(request)
        if not isinstance(response, Response):
            response = Response(response)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)
