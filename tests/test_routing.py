# tests/test_routing.py

import unittest
from dustapi.routing import Router
from werkzeug.wrappers import Request

class TestRouter(unittest.TestCase):
    def setUp(self):
        self.router = Router()

    def test_add_route(self):
        self.router.add_route('/test', lambda req: "Test", ["GET"])
        self.assertIn('/test', self.router.routes)

    def test_dispatch(self):
        self.router.add_route('/test', lambda req: "Test", ["GET"])
        request = Request({
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/test',
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '5000',
            'wsgi.input': None,
        })
        response = self.router.dispatch(request)
        self.assertEqual(response.data, b"Test")

if __name__ == '__main__':
    unittest.main()
