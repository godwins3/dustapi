import unittest
from dustapi.responses import Response, JsonResponse, HtmlResponse

class TestResponses(unittest.TestCase):
    def test_response(self):
        response = Response("Test Response")
        self.assertEqual(response.data, b"Test Response")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'text/plain')

    def test_json_response(self):
        data = {"key": "value"}
        response = JsonResponse(data)
        self.assertEqual(response.data, b'{"key": "value"}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')

    def test_html_response(self):
        html = "<p>Test HTML</p>"
        response = HtmlResponse(html)
        self.assertEqual(response.data, b"<p>Test HTML</p>")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'text/html')

if __name__ == '__main__':
    unittest.main()
