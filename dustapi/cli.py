import click
from dustapi.application import Dust
import os
import importlib.util
import sys

@click.group()
def cli():
    """DustAPI CLI: A command-line interface for the DustAPI web framework."""
    pass

@cli.command()
@click.option('--host', default='127.0.0.1', help='Host to run the server on.')
@click.option('--port', default=5000, type=int, help='Port to run the server on.')
@click.option('--template-folder', default='templates', help='Folder to look for templates.')
@click.option('--static-folder', default='static', help='Folder to serve static files from.')
@click.option('--log-file', default='app.log', help='File to log requests.')
def runserver(host, port, template_folder, static_folder, log_file):
    """Run the dustapi development server."""
    app_module_path = os.path.join(os.getcwd(), 'app.py')
    
    if not os.path.exists(app_module_path):
        click.echo("Error: app.py not found in the current working directory.", err=True)
        sys.exit(1)
    
    try:
        spec = importlib.util.spec_from_file_location("app", app_module_path)
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
    except Exception as e:
        click.echo(f"Error loading app.py: {str(e)}", err=True)
        sys.exit(1)
    
    if not hasattr(app_module, 'app') or not isinstance(app_module.app, Dust):
        click.echo("Error: 'app' instance of Dust class not found in app.py.", err=True)
        sys.exit(1)
    
    app = app_module.app
    app.template_folder = template_folder
    app.static_folder = static_folder
    app.log_file = log_file
    
    click.echo(f"Running server on {host}:{port} with templates from '{template_folder}', static files from '{static_folder}', and logging to '{log_file}'")
    app.run(host=host, port=port)

@cli.command()
@click.argument('project_name')
def createproject(project_name):
    """Create a new DustAPI project structure."""
    try:
        os.makedirs(project_name)
        os.makedirs(os.path.join(project_name, 'templates'))
        os.makedirs(os.path.join(project_name, 'static'))
        os.makedirs(os.path.join(project_name, 'uploads'))
        
        with open(os.path.join(project_name, 'templates', 'index.html'), 'w') as f:
            f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
</head>
<body>
    <h1>{{ heading }}</h1>
    <p>{{ content }}</p>
</body>
</html>
""")
        with open(os.path.join(project_name, 'app.py'), 'w') as f:
            f.write("""from dustapi.application import Dust, get_request
from dustapi.responses import JsonResponse, HtmlResponse, Response
import os

app = Dust()

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def save_uploaded_file(file_data, upload_folder):
    filename = file_data['filename']
    filepath = os.path.join(upload_folder, filename)
    with open(filepath, 'wb') as f:
        f.write(file_data['content'])
    return filename

@app.route('/', methods=['GET'])
async def home():
    return app.render_template('index.html', title="Home", heading="Welcome to dustapi Framework", content="This is the home page.")

@app.route('/hello', methods=['GET'])
async def hello():
    return "Hello, World!"

@app.route('/json', methods=['GET'])
async def json_example():
    data = {"message": "This is a JSON response"}
    return JsonResponse(data)

@app.route('/data', methods=['POST'])
async def post_data():
    return "Data received via POST"

@app.route('/update', methods=['PUT'])
async def update_data():
    return "Data received via PUT"

@app.route('/delete', methods=['DELETE'])
async def delete_data():
    return "Data received via DELETE"

@app.route('/upload', methods=['POST'])
async def upload_file():
    request = get_request()
    if 'file' not in request.form:
        raise ValueError("No file part in the request")
    
    file_data = request.form['file']
    filename = file_data['filename']
    filepath = save_uploaded_file(file_data, UPLOAD_FOLDER)

    return f"File {filename} uploaded successfully"

@app.websocket('/ws')
async def echo(websocket, path):
    async for message in websocket:
        await websocket.send(f"Echo: {message}")

@app.errorhandler(ValueError)
def handle_value_error(exc):
    return Response(str(exc), status=400)

@app.errorhandler(Exception)
def handle_generic_exception(exc):
    return Response("An unexpected error occurred.", status=500)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
""")
        click.echo(f"Project {project_name} created successfully.")
    except OSError as e:
        click.echo(f"Error creating project: {str(e)}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()
