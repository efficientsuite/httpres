import json
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from base64 import b64encode, b64decode

# Function to encrypt JSON data
def encrypt_json(data, password):
    # Convert the JSON data to a string and then to bytes
    json_data = json.dumps(data).encode('utf-8')

    # Generate a random salt
    salt = os.urandom(16)

    # Derive a key from the password using PBKDF2
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())

    # Generate a random nonce
    nonce = os.urandom(12)

    # Encrypt the data
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(json_data) + encryptor.finalize()

    # Return the encrypted data, nonce, and salt (all base64 encoded)
    return {
        'ciphertext': b64encode(ciphertext).decode('utf-8'),
        'nonce': b64encode(nonce).decode('utf-8'),
        'salt': b64encode(salt).decode('utf-8'),
        'tag': b64encode(encryptor.tag).decode('utf-8')
    }

# Function to decrypt JSON data
def decrypt_json(encrypted_data, password):
    success = False
    
    # Decode the base64 encoded values
    ciphertext = b64decode(encrypted_data['ciphertext'])
    nonce = b64decode(encrypted_data['nonce'])
    salt = b64decode(encrypted_data['salt'])
    tag = b64decode(encrypted_data['tag'])

    # Derive the key using the same method as encryption
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())

    # Decrypt the data
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
    if decrypted_data:
        success = True

    # Convert bytes back to JSON
    return json.loads(decrypted_data.decode('utf-8')), success