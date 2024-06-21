# examples/app.py

from dust.application import Application
from dust.responses import JsonResponse, HtmlResponse

app = Application()

@app.route('/')
def home(request):
    return HtmlResponse("<h1>Welcome to My Web Framework!</h1>")

@app.route('/hello')
def hello(request):
    return "Hello, World!"

@app.route('/json')
def json_example(request):
    data = {"message": "This is a JSON response"}
    return JsonResponse(data)

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 5000, app)
