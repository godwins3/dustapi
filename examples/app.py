from dust.application import Application, get_request
from dust.responses import JsonResponse, HtmlResponse, Response
from dust.helpers import save_uploaded_file, create_response, render_template
import os

app = Application()

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/', methods=['GET'], summary="Home Route", description="Returns the home page.", responses={200: {"description": "successful operation"}})
async def home():
    return render_template(app, 'index.html', title="Home", heading="Welcome to Dust Framework", content="This is the home page.")

@app.route('/hello', methods=['GET'], summary="Hello Route", description="Returns a hello message.", responses={200: {"description": "successful operation"}})
async def hello():
    return "Hello, World!"

@app.route('/json', methods=['GET'], summary="JSON Example", description="Returns a JSON response.", responses={200: {"description": "successful operation", "schema": {"type": "object", "properties": {"message": {"type": "string"}}}}})
async def json_example():
    data = {"message": "This is a JSON response"}
    return create_response(data)

@app.route('/login', methods=['POST'], summary="Login", description="Authenticates a user and returns a JWT.", responses={200: {"description": "successful operation", "schema": {"type": "object", "properties": {"token": {"type": "string"}}}}, 401: {"description": "Invalid credentials"}})
async def login():
    request = get_request()
    username = request.form.get('username')
    password = request.form.get('password')
    if username == 'user' and password == 'pass':
        token = app.jwt_handler.encode({'username': username})
        return create_response({'token': token})
    return create_response({'message': 'Invalid credentials'}, status=401)

@app.route('/protected', methods=['GET'], summary="Protected Route", description="Requires a valid JWT to access.", responses={200: {"description": "successful operation"}, 401: {"description": "Invalid token"}})
async def protected():
    request = get_request()
    token = request.headers.get('Authorization')
    if not token:
        return create_response({'message': 'Token is missing'}, status=401)
    
    token = token.split(" ")[1]
    payload, error = app.jwt_handler.decode(token)
    if error:
        return create_response({'message': error}, status=401)
    
    return create_response({'message': 'This is a protected route', 'user': payload['username']})

@app.route('/data', methods=['POST'], summary="Post Data", description="Receives data via POST and stores it in session.", responses={200: {"description": "Data received via POST"}})
async def post_data():
    request = get_request()
    request.session['data'] = 'This is session data'
    return "Data received via POST"

@app.route('/session', methods=['GET'], summary="Session Example", description="Returns session data.", responses={200: {"description": "Returns session data"}})
async def session_example():
    request = get_request()
    session_data = request.session.get('data', 'No session data')
    return f"Session Data: {session_data}"

@app.route('/update', methods=['PUT'], summary="Update Data", description="Receives data via PUT.", responses={200: {"description": "Data received via PUT"}})
async def update_data():
    return "Data received via PUT"

@app.route('/delete', methods=['DELETE'], summary="Delete Data", description="Receives data via DELETE.", responses={200: {"description": "Data received via DELETE"}})
async def delete_data():
    return "Data received via DELETE"

@app.route('/upload', methods=['POST'], summary="Upload File", description="Uploads a file.", responses={200: {"description": "File uploaded successfully"}}, parameters=[{"name": "file", "in": "formData", "type": "file", "required": True, "description": "The file to upload"}])
async def upload_file():
    request = get_request()
    if 'file' not in request.form:
        raise ValueError("No file part in the request")
    
    file_data = request.form['file']
    filename = save_uploaded_file(file_data, UPLOAD_FOLDER)

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
