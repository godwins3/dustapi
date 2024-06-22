from werkzeug.wrappers import Response

class Router:
    def __init__(self):
        self.routes = {}

    def add_route(self, path, handler, methods):
        self.routes[path] = (handler, methods)

    def dispatch(self, request):
        handler, methods = self.routes.get(request.path, (None, None))
        if handler and request.method in methods:
            response = handler(request)
            if isinstance(response, Response):
                return response
            return Response(response)
        return Response("Not Found", status=404)
