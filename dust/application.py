from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from .routing import Router
from .websockets import WebSocketRouter
import asyncio
import websockets
import threading
import os

class Application:
    def __init__(self):
        self.router = Router()
        self.ws_router = WebSocketRouter()

    def route(self, path, methods=["GET"]):
        def wrapper(handler):
            self.router.add_route(path, handler, methods)
            return handler
        return wrapper

    def websocket(self, path):
        def wrapper(handler):
            self.ws_router.add_route(path, handler)
            return handler
        return wrapper

    def parse_form_data(self, environ):
        form = {}
        content_type = environ.get('CONTENT_TYPE', '')

        if content_type.startswith('multipart/form-data'):
            from werkzeug.formparser import parse_form_data
            stream, form, files = parse_form_data(environ)
            for key, value in form.items():
                form[key] = value[0] if len(value) == 1 else value

            for key, file in files.items():
                filename = os.path.basename(file.filename)
                form[key] = {
                    'filename': filename,
                    'content_type': file.content_type,
                    'content': file.stream.read()
                }

        return form

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        request.form = self.parse_form_data(environ)

        response = self.router.dispatch(request)
        if not isinstance(response, Response):
            response = Response(response)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def run(self, host='localhost', port=5000):
        def run_http():
            run_simple(host, port, self)

        def run_ws():
            asyncio.run(websockets.serve(self.ws_router.handler, host, port + 1))

        threading.Thread(target=run_http).start()
        threading.Thread(target=run_ws).start()
