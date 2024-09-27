# fhe_operations.py
import simplefhe

# Key generation
def generate_keys():
    context = simplefhe.Context()
    secret_key = simplefhe.SecretKey(context)
    public_key = simplefhe.PublicKey(context)
    return context, secret_key, public_key

context, secret_key, public_key = generate_keys()

# Encryption
def encrypt_data(data, public_key):
    encrypted_data = [public_key.encrypt(value) for value in data]
    return encrypted_data

# Decryption
def decrypt_data(encrypted_data, secret_key):
    decrypted_data = [secret_key.decrypt(value) for value in encrypted_data]
    return decrypted_data
