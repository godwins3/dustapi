from werkzeug.wrappers import Response as WerkzeugResponse
    
class Router:
    def __init__(self):
        self.routes = []

    def add_route(self, path, handler, methods):
        self.routes.append((path, handler, methods))

    async def dispatch(self, request):
        for path, handler, methods in self.routes:
            if request.path == path and request.method in methods:
                return await handler(request)
        return WerkzeugResponse("Not Found", status=404)

