# examples/app.py

from dustapi.application import Dust, Response
from dustapi.sessions import SessionManager

# Initialize your Dust application with a session interface
app = Dust(secret_key=SessionManager(secret_key='super_secret_key'))

# Define routes using the `route` decorator
@app.route('/')
async def index():
    # Example of reading from session
    count = app.get_request().session.get('count', 0)
    app.get_request().session['count'] = count + 1  # Example of writing to session
    return app.render_template('index.html', title='Home', content='Welcome to Dust Framework!', count=count)

@app.route('/login', methods=['POST'])
async def login():
    # Example of handling form submission and setting session data
    form_data = app.get_request().form
    username = form_data.get('username')
    # Simulate authentication (replace with actual logic)
    if username == 'admin':
        app.get_request().session['user'] = username
        return Response("Login successful!", status=200)
    else:
        return Response("Invalid credentials", status=401)

@app.route('/logout')
async def logout():
    # Example of clearing session data
    app.get_request().session.pop('user', None)
    return Response("Logged out successfully!")

# Run the application
if __name__ == '__main__':
    app.run()
