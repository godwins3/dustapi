# tests/test_application.py

import unittest
from dust.application import Application

class TestApplication(unittest.TestCase):
    def setUp(self):
        self.app = Application()

    def test_home_route(self):
        @self.app.route('/')
        def home(request):
            return "Welcome!"

        environ = {
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/',
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '5000',
            'wsgi.input': None,
        }
        response = self.app(environ, lambda x, y: None)
        self.assertEqual(response[0], b"Welcome!")

if __name__ == '__main__':
    unittest.main()
