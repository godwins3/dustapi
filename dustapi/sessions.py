import hashlib
import uuid
from cryptography.fernet import Fernet

class SessionManager:
    def __init__(self, secret_key):
        self.sessions = {}
        self.secret_key = secret_key.encode('utf-8')
        self.cipher_suite = Fernet(self.secret_key)

    def generate_session_id(self):
        return str(uuid.uuid4())

    def create_session(self, data):
        session_id = self.generate_session_id()
        encrypted_data = self.encrypt_data(data)
        self.sessions[session_id] = encrypted_data
        return session_id

    def get_session(self, session_id):
        if session_id in self.sessions:
            decrypted_data = self.decrypt_data(self.sessions[session_id])
            return decrypted_data
        return None

    def delete_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]

    def encrypt_data(self, data):
        encrypted_data = self.cipher_suite.encrypt(data.encode('utf-8'))
        return encrypted_data.decode('utf-8')

    def decrypt_data(self, encrypted_data):
        decrypted_data = self.cipher_suite.decrypt(encrypted_data.encode('utf-8'))
        return decrypted_data.decode('utf-8')
