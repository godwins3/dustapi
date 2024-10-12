import asyncio
import signal
import threading
import os
import contextvars
import logging
from wsgiref.simple_server import make_server, WSGIRequestHandler, WSGIServer
from werkzeug.wrappers import Request, Response as WerkzeugResponse
from werkzeug.middleware.shared_data import SharedDataMiddleware
from jinja2 import Environment, FileSystemLoader, select_autoescape
from cryptography.fernet import Fernet
from .routing import Router
from .responses import Response
from .sessions import SessionManager
from .jwt import JWTHandler
from .openapi import OpenAPI
from .swagger_ui import SwaggerUI
# from .sse import SSE  # Import the SSE class we implemented
from goha.sse_engine import SSEEngine
# from .web_sockets import WebSocketRouter
from .web_sockets import WebSocketRouter

# Create a context variable to store the request
request_context = contextvars.ContextVar('request')

class Dust:
    def __init__(self, template_folder='templates', static_folder='static', static_url_path='/static', log_file='app.log', secret_key=None, jwt_secret_key=None):
        self.router = Router()
        self.template_env = Environment(
            loader=FileSystemLoader(template_folder),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self.static_folder = static_folder
        self.static_url_path = static_url_path
        self.error_handlers = {}
        self.logger = self.setup_logger(log_file)
        self.secret_key = secret_key or Fernet.generate_key().decode()
        self.session_interface = SessionManager(self.secret_key)
        self.jwt_handler = JWTHandler(jwt_secret_key)
        self.openapi = OpenAPI(title="dustapi Framework API", version="0.0.5", description="API documentation for dustapi Framework")
        self.sse = SSEEngine()  # Initialize the SSE object
        
        # Middleware to serve static files
        self.shared_data = SharedDataMiddleware(self.wsgi_app, {
            static_url_path: os.path.join(os.getcwd(), static_folder)
        })
        
        # Initialize SwaggerUI after shared_data is set up
        self.swagger_ui = SwaggerUI(self)
        
        self.http_thread = None
        self.stop_event = threading.Event()
        
        self.websocket_router = WebSocketRouter()
        self.http_server = None
        self.websocket_server = None

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
    
    def render_template(self, template_name, **context):
        try:
            template = self.template_env.get_template(template_name)
            return Response(template.render(context), content_type='text/html')
        except Exception as e:
            self.logger.error(f"Error rendering template {template_name}: {e}")
            raise

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
        self.logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return WerkzeugResponse("Internal Server Error", status=500)

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
                if isinstance(response, Response):
                    response = WerkzeugResponse(response.body, status=response.status, content_type=response.content_type)
                else:
                    response = WerkzeugResponse(response)
        except Exception as exc:
            response = self.handle_exception(exc)

        self.log_request(request, response)  # Log the request details

        if self.session_interface:
            session_id = request.cookies.get('session_id')
            if session_id and request.session:
                self.session_interface.save_session(session_id, request.session)

        request_context.reset(token)  # Reset the context
        return response(environ, start_response)

    def wsgi_app(self, environ, start_response):
        return asyncio.run(self.async_wsgi_app(environ, start_response))

    def __call__(self, environ, start_response):
        return self.shared_data(environ, start_response)

    def stop(self):
        self.stop_event.set()
        if self.http_server:
            self.http_server.shutdown()
        if self.websocket_server:
            self.websocket_router.stop_server()
        self.logger.info('Dust server gracefully stopped')

    def run(self, host='localhost', port=5000, websocket_port=5001):
        def run_http():
            with make_server(host, port, self) as httpd:
                self.http_server = httpd
                self.logger.info(f"Serving HTTP on {host}:{port}")
                while not self.stop_event.is_set():
                    httpd.handle_request()

        def run_websocket():
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop()
            self.websocket_server = loop.run_until_complete(self.websocket_router.start_server(host, websocket_port))
            self.logger.info(f"Serving WebSocket on {host}:{websocket_port}")
            loop.run_forever()

        self.http_thread = threading.Thread(target=run_http)
        self.websocket_thread = threading.Thread(target=run_websocket)

        self.http_thread.start()
        self.websocket_thread.start()

        def handle_sigint(signum, frame):
            self.stop()

        signal.signal(signal.SIGINT, handle_sigint)

        try:
            while not self.stop_event.is_set():
                if input().strip().lower() == 'q':
                    self.stop()
                    break
        except EOFError:
            self.stop()

        self.http_thread.join()
        self.websocket_thread.join()

    def setup_sse(self, key):
        """
        Set up the Searchable Symmetric Encryption with the given key.
        """
        self.sse.setup(key)

    def sse_encrypt(self, plaintext):
        """
        Encrypt the given plaintext using SSE.
        """
        return self.sse.encrypt(plaintext)

    def sse_search(self, keyword):
        """
        Search for encrypted documents containing the given keyword.
        """
        return self.sse.search(keyword)

    def websocket(self, path):
        def wrapper(handler):
            self.websocket_router.add_route(path, handler)
            return handler
        return wrapper

def get_request():
    return request_context.get()
