from werkzeug.middleware.session import SessionInterface
from werkzeug.contrib.securecookie import SecureCookieSession

class SecureCookieSessionInterface(SessionInterface):
    def __init__(self, secret_key):
        self.secret_key = secret_key

    def open_session(self, request):
        return SecureCookieSession.load_cookie(request, self.secret_key)

    def save_session(self, request, response, session):
        session.save_cookie(response)
