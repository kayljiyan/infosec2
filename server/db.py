# modules used
from dotenv import load_dotenv
from typing import Any
from security import verify_password
import os, psycopg2, schemas

user_structure = [ "user_name", "user_email", "hashed_password" ]

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


def insert_new_user(fname: str, mname: str, lname: str, password: str, email: str) -> None:
    """
    Inserts a new user into the users table

    Args:
        fname (str): user first name
        mname (str): user middle name
        lname (str): user last name
        password (str):  user password
        email (str): user email
    """
    with conn.cursor() as cur:
        cur.execute("INSERT INTO users (user_fname, user_mname, user_lname, user_password, user_email) VALUES (%s,%s,%s,%s,%s)",
                        (fname,
                        mname,
                        lname,
                        password,
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

def get_user(email: str) -> schemas.UserInDB | None:
    """
    Gets a user from the users table

    Args:
        email (str): user email

    Returns:
        Tuple[str, str, str] | None: a tuple containing the user's name, and email if the email exists, None otherwise
    """
    with conn.cursor() as cur:
        cur.execute("SELECT CONCAT(user_lname, ', ', user_fname, ' ', user_mname) AS user_name, user_email, user_password FROM users WHERE user_email=(%s)", (email,))
        user = cur.fetchone()
        if user is not None:
            user_dict = { user_structure[i] : user[i] for i, _ in enumerate(user) }
            return schemas.UserInDB(**user_dict)
        else:
            return None
    
def authenticate_user(email: str, password: str):
    """
    Authenticates a user

    Args:
        email (str): user email
    """
    user = get_user(email)
    # print(user)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
