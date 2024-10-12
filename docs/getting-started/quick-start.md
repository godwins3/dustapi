# Quick Start

This guide will help you create a simple DustAPI application.

## Creating a New Project

You can use the DustAPI CLI to create a new project:

```bash
dustapi createproject my_project
```

## Basic Application

Here's a simple DustAPI application:


```python
from dustapi import Dust

app = Dust()

@app.get("/")
def index():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(host="localhost", port=5000)
```

Save this as `app.py` and run it:

```bash
python app.py
```

Your application will be available at `http://127.0.0.1:5000`.
