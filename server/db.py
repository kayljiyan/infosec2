# modules used
from dotenv import load_dotenv
from typing import Any, Tuple
import os, psycopg2

# loads the environment variables
load_dotenv()

# environment variables
database: str = os.environ.get('POSTGRES_DATABASE')
host: str = os.environ.get('POSTGRES_HOST')
user:str = os.environ.get('POSTGRES_USER')
password: str = os.environ.get('POSTGRES_PASSWORD')
port: str = os.environ.get('POSTGRES_PORT')

# database connection
conn = psycopg2.connect(database=os.environ.get('POSTGRES_DATABASE'),
                        host=os.environ.get('POSTGRES_HOST'),
                        user=os.environ.get('POSTGRES_USER'),
                        password=os.environ.get('POSTGRES_PASSWORD'),
                        port=os.environ.get('POSTGRES_PORT'))


def insert_new_user(email: str, username: str, password: str, key: str, today: Any) -> None:
    """
    Inserts a new user into the users table

    Args:
        email (str): user email
        username (str): unique user name
        password (str): strong password
        key (str): key used to encrypt the password
        today (Any): date today
    """
    with conn.cursor() as cur:
        cur.execute("INSERT INTO users (user_email, user_name, user_password, password_key, created_at) VALUES (%s,%s,%s,%s,%s)",
                        (email,
                        username,
                        password,
                        key,
                        today))
    conn.commit()

def insert_new_token(token: str, secret: str, today: Any, email: str) -> None:
    """
    Inserts a new token into the tokens table

    Args:
        token (str): unique token
    """
    with conn.cursor() as cur:
        cur.execute("INSERT INTO tokens (user_token, token_secret, created_at, user_email) VALUES (%s,%s,%s,%s)",
                        (token,
                        secret,
                        today,
                        email))
    conn.commit()

def check_email_exists(email: str) -> bool:
    """
    Checks if an email exists in the users table

    Args:
        email (str): user email

    Returns:
        bool: True if the email exists, False otherwise
    """
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE user_email=(%s)", (email,))
        return cur.fetchone() is None

def check_username_exists(username: str) -> bool:
    """
    Checks if a username exists in the users table

    Args:
        username (str): unique user name
    """
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE user_name=(%s)", (username,))
        return cur.fetchone() is None

def find_token(token: str) -> Tuple[str, str] | None:
    """
    Checks if a token exists in the tokens table

    Args:
        token (str): unique token

    Returns:
        Tuple[str, str] | None: token and secret if the token exists, None otherwise
    """
    with conn.cursor() as cur:
        cur.execute("SELECT user_token, token_secret FROM tokens WHERE user_token=(%s)", (token,))
        return cur.fetchone()
    
def find_user(email: str) -> Tuple[str, str, str] | None:
    """
    Checks if an email exists in the users table

    Args:
        email (str): user email

    Returns:
        Tuple[str, str, str] | None: username, password, and key if the email exists, None otherwise
    """
    with conn.cursor() as cur:
        cur.execute("SELECT user_name, user_password, password_key FROM users WHERE user_email=(%s)", (email,))
        return cur.fetchone()
