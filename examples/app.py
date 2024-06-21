# examples/app.py

from dust.application import Application
from dust.responses import JsonResponse, HtmlResponse

app = Application()

@app.route('/', methods=['GET'])
def home(request):
    return HtmlResponse("<h1>Welcome to Dust Framework!</h1>")

@app.route('/hello', methods=['GET'])
def hello(request):
    return "Hello, World!"

@app.route('/json', methods=['GET'])
def json_example(request):
    data = {"message": "This is a JSON response"}
    return JsonResponse(data)

@app.route('/data', methods=['POST'])
def post_data(request):
    return "Data received via POST"

@app.route('/update', methods=['PUT'])
def update_data(request):
    return "Data received via PUT"

@app.route('/delete', methods=['DELETE'])
def delete_data(request):
    return "Data received via DELETE"

if __name__ == '__main__':
    app.run('localhost', 5000, app)
