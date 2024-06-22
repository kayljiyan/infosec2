from cryptography.fernet import Fernet
import secrets, string

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