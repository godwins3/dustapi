from werkzeug.wrappers import Response as WerkzeugResponse
import json

class Response(WerkzeugResponse):
    def __init__(self, response=None, status=200, headers=None, content_type='text/plain'):
        if headers is None:
            headers = {}
        headers['Content-Type'] = content_type
        super().__init__(response, status, headers)

class JsonResponse(Response):
    def __init__(self, data, status=200, headers=None):
        super().__init__(json.dumps(data), status, headers, content_type='application/json')

class HtmlResponse(Response):
    def __init__(self, html, status=200, headers=None):
        super().__init__(html, status, headers, content_type='text/html')
