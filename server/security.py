from datetime import timedelta, datetime, timezone
from password_strength import PasswordStats
from typing import Any
import jwt, consts, bcrypt

def check_password_strength(password: str) -> bool:
    """
    Checks the strength of a password

    Args:
        password (str): the password to be checked
    """
    return PasswordStats(password).strength() >= 0.66

def encrypt_password(plain_password: str) -> str:
    """
    Encrypts a password using the bcrypt algorithm

    Args:
        plain_password (str): the password to be encrypted

    Returns:
        str: the encrypted password
    """
    bytes = plain_password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a password using the bcrypt algorithm

    Args:
        plain_password (str): the password to be verified
        hashed_password (str): the hashed password to be verified
    """
    bytes = plain_password.encode('utf-8')
    hashed_password =  hashed_password.encode('utf-8')
    return bcrypt.checkpw(bytes, hashed_password)

def generate_access_token(payload: dict, expiry_date: timedelta | None = None) -> str:
    """
    Generates an access token

    Args:
        payload (dict): the payload to be encoded
        expiry_date (timedelta | None, optional): the expiry date of the token. Defaults to None.
    """
    to_encode = payload.copy()
    if expiry_date:
        expire = datetime.now(timezone.utc) + expiry_date
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, consts.SECRET_KEY, algorithm=consts.ALGORITHM)

def verify_access_token(token: str) -> dict:
    return jwt.decode(token, consts.SECRET_KEY, algorithms=[consts.ALGORITHM])