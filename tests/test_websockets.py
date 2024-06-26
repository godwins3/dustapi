# tests/test_websockets.py

import unittest
import asyncio
import websockets
from dustapi.application import Dust

class TestWebSockets(unittest.TestCase):
    def setUp(self):
        self.app = Dust()

    def test_echo_websocket(self):
        @self.app.websocket('/ws')
        async def echo(websocket, path):
            async for message in websocket:
                await websocket.send(f"Echo: {message}")

        async def test_client():
            uri = "ws://localhost:5001/ws"
            async with websockets.connect(uri) as websocket:
                await websocket.send("Hello, WebSocket!")
                response = await websocket.recv()
                self.assertEqual(response, "Echo: Hello, WebSocket!")

        asyncio.get_event_loop().run_until_complete(test_client())

if __name__ == '__main__':
    unittest.main()
