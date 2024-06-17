# modules used
from fastapi import FastAPI, Request, Response, status
from cryptography.fernet import Fernet
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from typing import Any, Coroutine, Tuple
import secrets, string, jwt, psycopg2, os

# loads the environment variables
load_dotenv()

# environment variables
database: str = os.environ.get('POSTGRES_DATABASE')
host: str = os.environ.get('POSTGRES_HOST')
user:str = os.environ.get('POSTGRES_USER')
password: str = os.environ.get('POSTGRES_PASSWORD')
port: str = os.environ.get('POSTGRES_PORT')

# creates the FastAPI app object
app: FastAPI = FastAPI()

# database connection
conn = psycopg2.connect(database=os.environ.get('POSTGRES_DATABASE'),
                        host=os.environ.get('POSTGRES_HOST'),
                        user=os.environ.get('POSTGRES_USER'),
                        password=os.environ.get('POSTGRES_PASSWORD'),
                        port=os.environ.get('POSTGRES_PORT'))

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

@app.get('/')
async def index(response: Response) -> dict:
    """
    Index page for the API

    Args:
        response (Response): response object to be returned in the header

    Returns:
        dict: hello world message
    """
    response.status_code = status.HTTP_200_OK
    return { 'message': 'Hello World' }

@app.post('/signup')
async def signup(request: Request, response: Response) -> dict:
    """
    Signs up a new user

    Args:
        request (Request): request body from the frontend
        response (Response): response object to be returned in the header

    Returns:
        dict: a dictionary containing an error message or the token and expiration date
    """
    data: Coroutine[str, str, str] = await request.json()
    username: str = data["username"]
    email: str = data["email"]
    password, key = encrypt_password(data["password"])
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE user_email=(%s)", (email,))
        if (cur.fetchone() is None):
            cur.execute("SELECT * FROM users WHERE user_name=(%s)", (username,))
            if (cur.fetchone() is None):
                secret: str = generate_secret()
                today: Any = datetime.today().date()
                expiry_date: Any = datetime.now(tz=timezone.utc) + timedelta(days=2)
                payload: dict = { "email": email, "password": password, "exp": expiry_date }
                token: str = jwt.encode(payload, secret) 
                cur.execute("INSERT INTO users (user_email, user_name, user_password, password_key, created_at) VALUES (%s,%s,%s,%s,%s)",
                            (email,
                            username,
                            password,
                            key,
                            today))
                cur.execute("INSERT INTO tokens (user_token, token_secret, created_at, user_email) VALUES (%s,%s,%s,%s)",
                            (token,
                            secret,
                            today,
                            email))
                response.status_code = status.HTTP_201_CREATED
                conn.commit()
                return { "JWT": token, "Expiry Date": expiry_date }
            else:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return { "message": "Username already exists" }
        else:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return { "message": "Email already exists" }

@app.post('/login')
async def login(request: Request, response: Response):
    """
    Logs in an existing user

    Args:
        request (Request): request body from the frontend
        response (Response): response object to be returned in the header

    Returns:
        dict: a dictionary containing an error message or a welcome message
    """
    data: Coroutine[Any, Any, Any] = await request.json()
    email: str = data["email"]
    password: str = data["password"]
    token: str = data["token"]
    with conn.cursor() as cur:
        cur.execute("SELECT user_token, token_secret FROM tokens WHERE user_token=(%s)", (token,))
        token = cur.fetchone()
        if (token is not None):
            try:
                jwt.decode(token[0], token[1], leeway=timedelta(seconds=10), algorithms=["HS256"])
                cur.execute("SELECT user_name, user_password, password_key FROM users WHERE user_email=(%s)", (email,))
                user: Tuple[str, str] = cur.fetchone()
                if (user is not None):
                    if (password == decrypt_password(user[1], user[2])):
                        response.status_code = status.HTTP_200_OK
                        conn.commit()
                        return { "message": f"Welcome {user[0]}" }
                    else:
                        response.status_code = status.HTTP_400_BAD_REQUEST
                        return { "message": "Incorrect password" }
                else:
                    response.status_code = status.HTTP_400_BAD_REQUEST
                    return { "message": "Email not found" }
            except jwt.ExpiredSignatureError:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return { "message": "Token expired" }
        else:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return { "message": "Token not found" }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", port=8000, reload=True)