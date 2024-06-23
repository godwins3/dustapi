from werkzeug.wrappers import Request #, Response
from werkzeug.wrappers import Response as WerkzeugResponse
from werkzeug.serving import run_simple
from werkzeug.middleware.shared_data import SharedDataMiddleware
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .routing import Router
from .web_sockets import WebSocketRouter
from .responses import Response
from .jwt import JWTHandler
from .openapi import OpenAPI
from .swagger_ui import SwaggerUI
from .sessions import SessionManager
import asyncio
import websockets
import threading
import os
import contextvars
import logging
import signal
import sys


# Create a context variable to store the request
request_context = contextvars.ContextVar('request')

class Application:
    def __init__(self, template_folder='templates', static_folder='static', static_url_path='/static', log_file='app.log', secret_key='supersecretkey', jwt_secret_key='jwtsecretkey', enable_sessions=False):
        self.router = Router()
        self.ws_router = WebSocketRouter()
        self.template_env = Environment(
            loader=FileSystemLoader(template_folder),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self.static_folder = static_folder
        self.static_url_path = static_url_path
        self.error_handlers = {}
        self.logger = self.setup_logger(log_file)
        self.secret_key = secret_key
        self.session_interface = SessionManager(secret_key) if enable_sessions else None
        self.jwt_handler = JWTHandler(jwt_secret_key)
        self.openapi = OpenAPI(title="dustapi Framework API", version="1.0.0", description="API documentation for dustapi Framework")
        # self.swagger_ui = SwaggerUI(self)

        # Middleware to serve static files
        self.shared_data = SharedDataMiddleware(self.wsgi_app, {
            static_url_path: os.path.join(os.getcwd(), static_folder)
        })

        # stop dust server
        signal.signal(signal.SIGINT, self.handle_stop_server)

    def handle_stop_server(self, signum, frame):
        print("Stopping server gracefully...")
        sys.exit(0)

    def setup_logger(self, log_file):
        logger = logging.getLogger('dustapi_logger')
        logger.setLevel(logging.INFO)

        # Create file handler which logs messages
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.INFO)

        # Create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)

        # Create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # Add the handlers to the logger
        logger.addHandler(fh)
        logger.addHandler(ch)

        return logger

    def log_request(self, request, response):
        self.logger.info(f'{request.method} {request.path} - {response.status_code}')

    def route(self, path, methods=["GET"], summary=None, description=None, responses=None, parameters=None, request_body=None):
        def wrapper(handler):
            async def wrapped_handler(*args, **kwargs):
                return await handler()
            self.router.add_route(path, wrapped_handler, methods)
            if summary and description and responses:
                for method in methods:
                    self.openapi.add_path(path, method, summary, description, responses, parameters, request_body)
            return handler
        return wrapper

    def websocket(self, path):
        def wrapper(handler):
            self.ws_router.add_route(path, handler)
            return handler
        return wrapper

    def render_template(self, template_name, **context):
        template = self.template_env.get_template(template_name)
        return template.render(context)

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

    def handle_exception(self, exc):
        handler = self.error_handlers.get(type(exc))
        if handler:
            return handler(exc)
        return Response("Internal Server Error", status=500)

    def errorhandler(self, exc_class):
        def decorator(func):
            self.error_handlers[exc_class] = func
            return func
        return decorator

    async def async_wsgi_app(self, environ, start_response):
        request = Request(environ)
        request.form = self.parse_form_data(environ)
        
        if self.session_interface:
            session_id = request.cookies.get('session_id')
            request.session = self.session_interface.get_session(session_id) if session_id else None
        else:
            request.session = None
        
        token = request_context.set(request)  # Set the request context

        try:
            response = await self.router.dispatch(request)
            if not isinstance(response, WerkzeugResponse):
                response = WerkzeugResponse(response)
        except Exception as exc:
            response = self.handle_exception(exc)

        self.log_request(request, response)  # Log the request details
        
        if self.session_interface:
            session_id = request.cookies.get('session_id')
            self.session_interface.save_session(session_id, request.session)
        
        request_context.reset(token)  # Reset the context
        return response(environ, start_response)

    def wsgi_app(self, environ, start_response):
        return asyncio.run(self.async_wsgi_app(environ, start_response))

    def __call__(self, environ, start_response):
        return self.shared_data(environ, start_response)

    def run(self, host='localhost', port=5000):
        def run_http():
            run_simple(host, port, self)

        def run_ws():
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop()
            loop.run_until_complete(websockets.serve(self.ws_router.handler, host, port + 1))
            loop.run_forever()

        # Start HTTP server in a separate thread
        http_thread = threading.Thread(target=run_http)
        http_thread.start()

        # Start WebSocket server in a separate thread
        ws_thread = threading.Thread(target=run_ws)
        ws_thread.start()

        # Setup signal handler for Ctrl+C (SIGINT)
        signal.signal(signal.SIGINT, self.stop_server)

        # Wait for both threads to complete
        http_thread.join()
        ws_thread.join()

    def stop_server(self, signum, frame):
        print("Stopping servers...")

        # Perform cleanup tasks here if needed

        # Exit the application gracefully
        sys.exit(0)
        
def get_request():
    return request_context.get()
