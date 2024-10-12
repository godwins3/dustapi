# dustapi/websockets.py

import asyncio
from websockets.server import serve


class WebSocketRouter:
    def __init__(self):
        # Dictionary to store WebSocket routes
        self.routes = {}
        # WebSocket server instance
        self.server = None

    def add_route(self, path, handler):
        # Add a new WebSocket route with its corresponding handler
        self.routes[path] = handler

    async def handler(self, websocket, path):
        # Main WebSocket handler that routes incoming connections
        if path in self.routes:
            # If the path exists in routes, call the corresponding handler
            await self.routes[path](websocket, path)
        else:
            # If the path is not found, close the WebSocket connection
            await websocket.close()

    async def start_server(self, host, port):
        # Start the WebSocket server
        self.server = await serve(self.handler, host, port)
        # Wait until the server is closed
        await self.server.wait_closed()

    def stop_server(self):
        # Stop the WebSocket server if it's running
        if self.server:
            self.server.close()

