import jwt
from datetime import datetime, timedelta

class JWTHandler:
    def __init__(self, secret_key, algorithm='HS256', expiration_delta=timedelta(hours=1)):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expiration_delta = expiration_delta

    def encode(self, payload):
        payload['exp'] = datetime.utcnow() + self.expiration_delta
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload, None
        except jwt.ExpiredSignatureError:
            return None, 'Token has expired'
        except jwt.InvalidTokenError:
            return None, 'Invalid token'
