# dustapi/sessions.py
from cryptography.fernet import Fernet
import base64
import os

class SessionManager:
    def __init__(self, secret_key):
        self.secret_key = secret_key.encode()
        self.cipher_suite = Fernet(self.secret_key)
        self.sessions = {}  # This should be replaced by a more persistent store

    def create_session(self, session_data):
        session_id = base64.urlsafe_b64encode(os.urandom(24)).decode('utf-8')
        encrypted_data = self.cipher_suite.encrypt(session_data.encode())
        self.sessions[session_id] = encrypted_data
        return session_id

    def get_session(self, session_id):
        encrypted_data = self.sessions.get(session_id)
        if encrypted_data:
            decrypted_data = self.cipher_suite.decrypt(encrypted_data).decode()
            return eval(decrypted_data)  # Be careful with eval, it's just for example purposes
        return None

    def save_session(self, session_id, session_data):
        encrypted_data = self.cipher_suite.encrypt(str(session_data).encode())
        self.sessions[session_id] = encrypted_data

    def delete_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]