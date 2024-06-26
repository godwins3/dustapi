import asyncio
import signal
import threading
import os
import contextvars
import logging
from werkzeug.wrappers import Request, Response as WerkzeugResponse
from werkzeug.serving import run_simple
from werkzeug.middleware.shared_data import SharedDataMiddleware
from jinja2 import Environment, FileSystemLoader, select_autoescape
from cryptography.fernet import Fernet
from .routing import Router
from .web_sockets import WebSocketRouter
from .responses import Response
from .sessions import SessionManager
from .jwt import JWTHandler
from .openapi import OpenAPI
from .swagger_ui import SwaggerUI
import websockets

# Create a context variable to store the request
request_context = contextvars.ContextVar('request')

class Dust:
    def __init__(self, template_folder='templates', static_folder='static', static_url_path='/static', log_file='app.log', secret_key=None, jwt_secret_key='jwtsecretkey'):
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
        self.secret_key = secret_key or Fernet.generate_key().decode()
        self.session_interface = SessionManager(self.secret_key)
        self.jwt_handler = JWTHandler(jwt_secret_key)
        self.openapi = OpenAPI(title="dustapi Framework API", version="0.0.5", description="API documentation for dustapi Framework")
        
        # Middleware to serve static files
        self.shared_data = SharedDataMiddleware(self.wsgi_app, {
            static_url_path: os.path.join(os.getcwd(), static_folder)
        })
        
        # Initialize SwaggerUI after shared_data is set up
        self.swagger_ui = SwaggerUI(self)
        
        self.http_task = None
        self.ws_task = None
        self.stop_event = threading.Event()

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

    def wsgi_app(self, environ, start_response):
        return asyncio.run(self.async_wsgi_app(environ, start_response))

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

    def __call__(self, environ, start_response):
        return self.shared_data(environ, start_response)

    def stop(self):
        self.stop_event.set()
        if self.http_task:
            self.http_task.join()
        if self.ws_task:
            self.ws_task.cancel()
        print("Server stopped.")

    def run(self, host='localhost', port=5000):
        def run_http():
            run_simple(host, port, self)

        self.http_task = threading.Thread(target=run_http)
        self.http_task.start()

        try:
            self.ws_task = asyncio.run(self.run_ws(host, port))
        except KeyboardInterrupt:
            print("KeyboardInterrupt: Stopping the server...")
            self.stop()
            return

        def handle_sigint(signum, frame):
            self.stop()

        signal.signal(signal.SIGINT, handle_sigint)

        def listen_for_q():
            try:
                while not self.stop_event.is_set():
                    if input().strip().lower() == 'q':
                        self.stop()
                        break
            except EOFError:
                self.stop()

        threading.Thread(target=listen_for_q).start()

    async def run_ws(self, host, port):
        try:
            async with websockets.serve(self.ws_router.handler, host, port + 1):
                await self.stop_event.wait()
        except asyncio.CancelledError:
            print("WebSocket server task canceled.")
        except Exception as e:
            print(f"WebSocket server exception: {e}")

def get_request():
    return request_context.get()
