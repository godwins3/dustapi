# Routing

Routing in DustAPI is handled by the `Router` class. It allows you to map URL patterns to handler functions.

## Basic Routing

You can define routes using the `@app.route` decorator:

```python
@app.route("/")
def index():
    return "Welcome to DustAPI!"
```

This creates a route for the root URL ('/') that responds to GET requests.

## Route Parameters

DustAPI supports dynamic route parameters:

```python
@app.route("/user/<username>")
def show_user(username):
    return f"User: {username}"
```



## HTTP Methods

You can specify which HTTP methods a route should respond to:

```python
@app.route('/data', methods=['POST'])
async def post_data():
    return "Data received via POST"
```


## WebSocket Routes

DustAPI also supports WebSocket routes:

```python
@app.websocket('/ws')
async def echo(websocket, path):
    async for message in websocket:
        await websocket.send(f"Echo: {message}")
```

For more details on the routing system, see the `Router` class in the following file:

```python:tests/test_routing.py
startLine: 1
endLine: 28
```
