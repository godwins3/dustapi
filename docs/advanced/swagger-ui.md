# Swagger UI Integration

DustAPI includes built-in support for Swagger UI, which provides interactive API documentation.

## Enabling Swagger UI

Swagger UI is automatically enabled when you create a `Dust` application. By default, it's available at the `/docs` endpoint.

## OpenAPI Specification

The OpenAPI specification for your API is automatically generated based on your route definitions and docstrings. You can access the raw OpenAPI JSON at `/openapi.json`.

## Customizing API Documentation

You can add more detailed information to your API documentation by using docstrings and type hints in your route handlers:


## Accessing Swagger UI

Once your application is running, you can access the Swagger UI by navigating to `http://your-server-address/docs` in your web browser.

## Customizing Swagger UI

You can customize the Swagger UI by modifying the `SwaggerUI` class in your application:

```python
from dustapi.swagger_ui import SwaggerUI

class CustomSwaggerUI(SwaggerUI):
    def init(self, app, openapi_json_path='/custom_openapi.json',swagger_ui_path='/api_docs'):
        super().init(app, openapi_json_path, swagger_ui_path)

app = Dust(swagger_ui_class=CustomSwaggerUI)
```
