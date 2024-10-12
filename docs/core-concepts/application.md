# Application

The `Dust` class is the core of your DustAPI application. It handles routing, middleware, and serves as the ASGI application.

## Creating an Application

To create a DustAPI application, import the `Dust` class and instantiate it:

```python
from dustapi import Dust
app = Dust()
```

## Running the Application

You can run your application using the `run` method:

```python
app.run(host="localhost", port=5000)
```

## Application Configuration

The `Dust` class accepts several parameters for configuration:

- `template_folder`: The folder where your HTML templates are stored.
- `static_folder`: The folder for serving static files.
- `jwt_secret`: Secret key for JWT encoding/decoding.

Example:

```python
app = Dust(template_folder="templates", static_folder="static", jwt_secret="my_secret_key")
```

For more details on the `Dust` class, see the [API Reference](../api-reference/dust.md).
