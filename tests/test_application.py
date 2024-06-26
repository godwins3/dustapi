# tests/test_application.py

import unittest
from dustapi.application import Dust

class TestApplication(unittest.TestCase):
    def setUp(self):
        self.app = Dust()

    def test_home_route(self):
        @self.app.route('/')
        def home():
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

    def test_post_data_route(self):
        @self.app.route('/data', methods=['POST'])
        def post_data():
            return "Data received via POST"

        environ = {
            'REQUEST_METHOD': 'POST',
            'PATH_INFO': '/data',
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '5000',
            'wsgi.input': None,
        }
        response = self.app(environ, lambda x, y: None)
        self.assertEqual(response[0], b"Data received via POST")

    def test_update_data_route(self):
        @self.app.route('/update', methods=['PUT'])
        def update_data():
            return "Data received via PUT"

        environ = {
            'REQUEST_METHOD': 'PUT',
            'PATH_INFO': '/update',
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '5000',
            'wsgi.input': None,
        }
        response = self.app(environ, lambda x, y: None)
        self.assertEqual(response[0], b"Data received via PUT")

    def test_delete_data_route(self):
        @self.app.route('/delete', methods=['DELETE'])
        def delete_data():
            return "Data received via DELETE"

        environ = {
            'REQUEST_METHOD': 'DELETE',
            'PATH_INFO': '/delete',
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '5000',
            'wsgi.input': None,
        }
        response = self.app(environ, lambda x, y: None)
        self.assertEqual(response[0], b"Data received via DELETE")

if __name__ == '__main__':
    unittest.main()
