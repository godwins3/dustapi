# Server-Sent Events (SSE)

DustAPI supports Server-Sent Events (SSE), allowing the server to push data to the client in real-time.

## Creating an SSE Endpoint

To create an SSE endpoint, you can use the `SSEEngine` class:

```python
from dustapi.application import Dust
from dustapi.goha.sse_engine import SSEEngine
app = Dust()
sse = SSEEngine()
@app.route('/events')
async def sse_events():
    async def event_generator():
        for i in range(10):
            yield f"data: Event {i}\n\n"
            await asyncio.sleep(1)
    return sse.response(event_generator())
```

This creates an SSE endpoint at '/events' that sends 10 events, one per second.

## SSE Client

On the client-side, you can connect to the SSE endpoint like this:

```javascript
const eventSource = new EventSource('/events');

eventSource.onmessage = function(event) {
    console.log('Received event:', event.data);
};

eventSource.onerror = function(error) {
    console.error('EventSource failed:', error);
    eventSource.close();
};
```

## Custom Event Types

You can send custom event types:

```python
async def event_generator():
    yield "event: update\ndata: Update event\n\n"
    yield "event: message\ndata: Message event\n\n"

return sse.response(event_generator())
```

On the client-side, you can listen for specific event types:

```javascript
eventSource.addEventListener('update', function(event) {
    console.log('Received update:', event.data);
});

eventSource.addEventListener('message', function(event) {
    console.log('Received message:', event.data);
});
```

SSE provides a simple way to implement real-time updates from the server to the client.
