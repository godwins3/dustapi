import click
from dust.application import Application
import os

@click.group()
def cli():
    """Dust CLI: A command-line interface for the Dust web framework."""
    pass

@cli.command()
@click.option('--host', default='localhost', help='Host to run the server on.')
@click.option('--port', default=5000, help='Port to run the server on.')
@click.option('--template-folder', default='templates', help='Folder to look for templates.')
@click.option('--static-folder', default='static', help='Folder to serve static files from.')
@click.option('--log-file', default='app.log', help='File to log requests.')
def runserver(host, port, template_folder, static_folder, log_file):
    """Run the Dust development server."""
    app = Application(template_folder=template_folder, static_folder=static_folder, log_file=log_file)
    click.echo(f"Running server on {host}:{port} with templates from '{template_folder}', static files from '{static_folder}', and logging to '{log_file}'")
    app.run(host=host, port=port)

@cli.command()
def createproject():
    """Create a new Dust project structure."""
    project_name = click.prompt('Enter the project name')
    os.makedirs(project_name)
    os.makedirs(os.path.join(project_name, 'templates'))
    os.makedirs(os.path.join(project_name, 'static'))
    os.makedirs(os.path.join(project_name, 'uploads'))
    with open(os.path.join(project_name, 'app.py'), 'w') as f:
        f.write("""from dust.application import Application, get_request
from dust.responses import JsonResponse, HtmlResponse, Response
import os

app = Application()

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
    return app.render_template('example_template.html', title="Home", heading="Welcome to Dust Framework", content="This is the home page.")

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

# Custom error handler for ValueError
@app.errorhandler(ValueError)
def handle_value_error(exc):
    return Response(str(exc), status=400)

# Custom error handler for generic exceptions
@app.errorhandler(Exception)
def handle_generic_exception(exc):
    return Response("An unexpected error occurred.", status=500)

if __name__ == '__main__':
    app.run(host='localhost', port=5000)
""")
    click.echo(f"Project {project_name} created successfully.")

if __name__ == '__main__':
    cli()
