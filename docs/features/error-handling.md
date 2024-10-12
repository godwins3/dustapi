# Error Handling

DustAPI provides a robust error handling system that allows you to gracefully handle exceptions in your application.

## Basic Error Handling

You can use the `@app.errorhandler` decorator to register error handlers for specific exception types:

```python
from dustapi.application import Dust
from dustapi.responses import Response
app = Dust()
@app.errorhandler(ValueError)
def handle_value_error(exc):
    return Response(str(exc), status=400)

@app.errorhandler(Exception)
def handle_generic_exception(exc):
    return Response("An unexpected error occurred.", status=500)
```

In this example, we've registered handlers for the `ValueError` exception and a generic `Exception`.

## Custom Error Responses

You can customize the error responses to fit your application's needs:

```python
from dustapi.helpers import create_response

@app.errorhandler(404)
def not_found_error(exc):
    return create_response({"error": "Resource not found"}, status=404)
```

## Global Error Handling

For global error handling, you can use middleware or modify the `Dust` class to catch and handle exceptions globally.

## Logging Errors

It's a good practice to log errors for debugging purposes:

```python
import logging
from dustapi.logger import logger

@app.errorhandler(Exception)
def handle_exception(exc):
    logger.error(f"An error occurred: {str(exc)}")
    return Response("An unexpected error occurred.", status=500)
```

Remember to configure your logger appropriately for your application's needs.
