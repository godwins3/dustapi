# WebSockets

DustAPI provides built-in support for WebSockets, allowing real-time bidirectional communication between the client and server.

## Creating a WebSocket Route

You can create a WebSocket route using the `@app.websocket` decorator:

```python
@app.websocket('/ws')
async def echo(websocket, path):
    async for message in websocket:
        await websocket.send(f"Echo: {message}")
```

This creates a WebSocket endpoint at '/ws' that echoes back any message it receives.

## WebSocket Handlers

WebSocket handlers are asynchronous functions that take two parameters:

1. `websocket`: The WebSocket connection object.
2. `path`: The path of the WebSocket endpoint.

## Sending and Receiving Messages

- To send a message: `await websocket.send(message)`
- To receive a message: `message = await websocket.recv()`

## Example Usage

Here's an example of how to use WebSockets in your application:

```python:examples/sample_dust_app/app.py
startLine: 80
endLine: 83
```

For more details on WebSocket implementation, see the following test file:

```python:tests/test_websockets.py
startLine: 1
endLine: 28
```

