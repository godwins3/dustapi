# File Uploads

DustAPI supports file uploads, allowing you to handle file submissions from clients.

## Handling File Uploads

To handle file uploads, you can use the `request.form` object:

```python
from dustapi.application import get_request
from dustapi.helpers import save_uploaded_file

UPLOAD_FOLDER = 'uploads'

@app.route('/upload', methods=['POST'])
async def upload_file():
    request = get_request()
    if 'file' not in request.form:
        raise ValueError("No file part in the request")
    
    file_data = request.form['file']
    filename = save_uploaded_file(file_data, UPLOAD_FOLDER)

    return f"File {filename} uploaded successfully"
```

## Helper Functions

DustAPI provides helper functions to make file handling easier:

```python:dustapi/helpers.py
startLine: 1
endLine: 12
```

The `save_uploaded_file` function securely saves the uploaded file to the specified folder.

## Configuration

Make sure to set up your upload folder:

```python
UPLOAD_folder = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
```

## Security Considerations

- Always validate and sanitize file names before saving.
- Limit the size and types of files that can be uploaded.
- Store uploaded files outside of the web root to prevent direct access.

