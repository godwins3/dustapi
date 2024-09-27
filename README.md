# DustAPI - A Fast light weight Python Web Framework

DustAPI is a lightweight web framework written in Python, designed to be simple and easy to use. It provides basic routing and response handling, making it a great starting point for learning about web frameworks or building small web applications.

## Features

- Simple and intuitive routing
- Fully homomorphic encryption (i.e  dust server interacts with encrypted data without ever decrypting it)
- Support for all HTTP methods (GET, POST, PUT, DELETE, etc.)
- WebSocket support
- Custom response types (JSON, HTML, etc.)
- Extensible and lightweight
- Auto generate docs with swagger
- Support for jwt and session manager

## Pending features

Feel free to help by contributing on these features to make dustapi a success.

- AI/ML model inference and consumption
- Middleware support (planned)

## Installation

To install DustAPI, you can simply use pip:

```bash
pip install dustapi
```

## Usage

Here is a simple example of how to create a web application using dustapi:

### Create a dustapi project

```bash
dustapi createproject
```

### Run dustapi server

```bash
dustapi runserver --host 0.0.0.0 --port 8000 --template-folder mytemplates --static-folder mystatic --log-file myapp.log
```

### Example

```bash
from dustapi.application import Dust, get_request
from dustapi.responses import JsonResponse, HtmlResponse, Response
import os

app = Dust()

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def save_uploaded_file(file_data, upload_folder):
    filename = file_data['filename']
    filepath = os.path.join(upload_folder, filename)
    with open(filepath, 'wb') as f:
        f.write(file_data['content'])
    return filename

@app.route('/', methods=['GET'])
async def home():
    return app.render_template('index.html', title="Home", heading="Welcome to dustapi Framework", content="This is the home page.")

@app.route('/hello', methods=['GET'])
async def hello():
    return "Hello, World!"

@app.route('/json', methods=['GET'])
async def json_example():
    data = {"message": "This is a JSON response"}
    return JsonResponse(data)

@app.route('/data', methods=['POST'])
async def post_data():
    return "Data received via POST"

@app.route('/update', methods=['PUT'])
async def update_data():
    return "Data received via PUT"

@app.route('/delete', methods=['DELETE'])
async def delete_data():
    return "Data received via DELETE"

@app.route('/upload', methods=['POST'])
async def upload_file():
    request = get_request()
    if 'file' not in request.form:
        raise ValueError("No file part in the request")
    
    file_data = request.form['file']
    filename = file_data['filename']
    filepath = save_uploaded_file(file_data, UPLOAD_FOLDER)

    return f"File {filename} uploaded successfully"

# Custom error handler for ValueError
@app.errorhandler(ValueError)
def handle_value_error(exc):
    return Response(str(exc), status=400)

# Custom error handler for generic exceptions
@app.errorhandler(Exception)
def handle_generic_exception(exc):
    return Response("An unexpected error occurred.", status=500)

if __name__ == '__main__':
    app.run(host='localhost', port=5000)

```
