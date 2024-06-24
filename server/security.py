from cryptography.fernet import Fernet
from typing import Any
from datetime import timedelta
import secrets, string, jwt

def generate_secret() -> str:
    """
    Generates a 32-character string of random alphanumeric characters

    Returns:
        str: secret key to be used to generate a token
    """
    alphabet = string.ascii_letters + string.digits 
    secret = ''.join(secrets.choice(alphabet) for i in range(32))
    return secret

def encrypt_password(password: str) -> str:
    """
    Encrypts a password using the Fernet encryption algorithm

    Args:
        password (str): plaintext password from user request

    Returns:
        str: the encrypted password
        str: the key used for encryption
    """
    key: bytes = Fernet.generate_key()
    fernet: Fernet = Fernet(key)
    encPass: bytes = fernet.encrypt(password.encode())
    return encPass.decode("latin-1"), key.decode("latin-1")

def decrypt_password(password: str, key: str) -> str:
    """
    Decrypts a password using the Fernet decryption algorithm

    Args:
        password (str): plaintext password from user request
        key (str): key used to encrypt password from user request

    Returns:
        str: the decrypted password
    """
    fernet: Fernet = Fernet(key)
    decPass: bytes = fernet.decrypt(password.encode())
    return decPass.decode("latin-1")

def generate_token(payload: dict, secret: str) -> str:
    """
    Generates a token using the JWT algorithm

    Args:
        payload (dict): dictionary containing user information
        secret (str): secret key to be used to generate a token

    Returns:
        str: the generated token
    """
    return jwt.encode(payload, secret)

def verify_token(token: str, secret: str) -> Any:
    """
    Verifies a token using the JWT algorithm

    Args:
        token (str): unique token
        
    Returns:
        dict: dictionary containing user information
    """
    return jwt.decode(token, secret, leeway=timedelta(seconds=10), algorithms=["HS256"])