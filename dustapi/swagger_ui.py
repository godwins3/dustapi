from werkzeug.wrappers import Response
from werkzeug.middleware.shared_data import SharedDataMiddleware
import os

class SwaggerUI:
    def __init__(self, app, openapi_json_path='/openapi.json', swagger_ui_path='/docs'):
        self.app = app
        self.openapi_json_path = openapi_json_path
        self.swagger_ui_path = swagger_ui_path
        self.add_swagger_routes()

    def add_swagger_routes(self):
        # Route to serve the OpenAPI JSON
        self.app.route(self.openapi_json_path, methods=['GET'])(self.serve_openapi_json)

        # Route to serve the Swagger UI
        self.app.route(self.swagger_ui_path, methods=['GET'])(self.serve_swagger_ui)

        # Serve the static Swagger UI files
        swagger_ui_dir = os.path.join(os.path.dirname(__file__), 'static', 'swagger-ui')
        self.app.shared_data = SharedDataMiddleware(self.app.shared_data, {
            '/swagger-ui': swagger_ui_dir
        })

    async def serve_openapi_json(self):
        openapi_json = self.app.openapi.generate()
        return Response(openapi_json, mimetype='application/json')

    async def serve_swagger_ui(self):
        with open(os.path.join(os.path.dirname(__file__), 'static', 'swagger-ui', 'index.html'), 'r') as f:
            content = f.read()
        return Response(content, mimetype='text/html')
