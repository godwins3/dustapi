# examples/app.py

from dust.application import Application
from dust.responses import JsonResponse, HtmlResponse
import asyncio

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

@app.websocket('/ws')
async def echo(websocket, path):
    async for message in websocket:
        await websocket.send(f"Echo: {message}")

if __name__ == '__main__':
    app.run(host='localhost', port=5000)
