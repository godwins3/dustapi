# dust/application.py

from werkzeug.wrappers import Request
from werkzeug.serving import run_simple
from .routing import Router
from .responses import Response
from .websockets import WebSocketRouter
import asyncio
import websockets
import threading

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

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
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
            asyncio.run(websockets.serve(self.ws_router.handler, host, port+1))

        threading.Thread(target=run_http).start()
        threading.Thread(target=run_ws).start()
