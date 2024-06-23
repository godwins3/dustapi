# dustapi/websockets.py

import asyncio
from websockets.legacy.server import WebSocketServer


class WebSocketRouter:
    def __init__(self):
        self.routes = {}

    def add_route(self, path, handler):
        self.routes[path] = handler

    async def handler(self, websocket, path):
        if path in self.routes:
            await self.routes[path](websocket, path)
        else:
            await WebSocketServer.close()
