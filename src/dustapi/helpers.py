import os
import json
from .responses import JsonResponse
from werkzeug.utils import secure_filename

def save_uploaded_file(file_data, upload_folder):
    """Save uploaded file to the specified folder."""
    filename = secure_filename(file_data['filename'])
    filepath = os.path.join(upload_folder, filename)
    with open(filepath, 'wb') as f:
        f.write(file_data['content'])
    return filename

def create_response(data, status=200, content_type='application/json'):
    """Create a response with the given data."""
    if content_type == 'application/json':
        response_data = json.dumps(data)
    else:
        response_data = data
    return JsonResponse(response_data, status=status, content_type=content_type)

def render_template(app, template_name, **context):
    """Render a template with the given context."""
    return app.render_template(template_name, **context)
