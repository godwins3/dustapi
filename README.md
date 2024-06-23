# dustapi - A Simple Python Web Framework

dustapi is a lightweight web framework written in Python, designed to be simple and easy to use. It provides basic routing and response handling, making it a great starting point for learning about web frameworks or building small web applications.

## Features

- Simple and intuitive routing
- Support for all HTTP methods (GET, POST, PUT, DELETE, etc.)
- WebSocket support
- Custom response types (JSON, HTML, etc.)
- Middleware support (planned)
- Extensible and lightweight
- Auto generate docs with swagger
- Support for jwt and session manager

## Installation

To install dustapi, you can simply use pip:

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
# examples/app.py

from dustapi.application import Application
from dustapi.responses import JsonResponse, HtmlResponse

app = Application()

@app.route('/')
def home():
    return HtmlResponse("<h1>Welcome to dustapi Framework!</h1>")

@app.route('/hello')
def hello():
    return "Hello, World!"

@app.route('/json')
def json_example():
    data = {"message": "This is a JSON response"}
    return JsonResponse(data)

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 5000, app)
```
