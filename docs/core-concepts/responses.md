# Responses

DustAPI provides several types of responses to handle different scenarios.

## Basic Response

The `Response` class is the base class for all responses:

```python
from dustapi.responses import Response

@app.route('/')
async def home():
    return Response("Welcome to DustAPI!")
```

## JSON Response

For API endpoints, you can use `JsonResponse`:

```python
from dustapi.responses import JsonResponse

@app.route('/api/data')
async def get_data():
    data = {"key": "value"}
    return JsonResponse(data)
```

## HTML Response

For rendering HTML, use `HtmlResponse`:

```python
from dustapi.responses import HtmlResponse

@app.route('/page')
async def page():
    return HtmlResponse("<h1>Welcome to my page!</h1>")
```

## Custom Responses

You can create custom responses using the `create_response` helper function:

```python
from dustapi.helpers import create_response

@app.route('/custom')
async def custom():
    return create_response({"message": "Custom response"}, status=201, content_type='application/json')
```

For more details on response types, see the following file:

```python:tests/test_responses.py
startLine: 1
endLine: 26
```

