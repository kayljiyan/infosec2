# modules used
from fastapi import FastAPI, Request, Response, status
from datetime import datetime, timedelta, timezone
from typing import Any, Coroutine, Tuple
from security import generate_secret, encrypt_password, decrypt_password, generate_token, verify_token
from db import conn, check_email_exists, check_username_exists, find_token, find_user, insert_new_user, insert_new_token
import jwt

# creates the FastAPI app object
app: FastAPI = FastAPI()

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

@app.post('/api/v1/signup')
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
    if (check_email_exists(email)):
        if (check_username_exists(username)):
            secret: str = generate_secret()
            today: Any = datetime.today().date()
            expiry_date: Any = datetime.now(tz=timezone.utc) + timedelta(days=2)
            payload: dict = { "username": username, "email": email, "password": password, "exp": expiry_date }
            token: str = generate_token(payload, secret) 
            insert_new_user(email, username, password, key, today)
            insert_new_token(token, secret, today, email)
            response.status_code = status.HTTP_201_CREATED
            return { "JWT": token, "Expiry Date": expiry_date }
        else:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return { "message": "Username already exists" }
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Email already exists" }

@app.post('/api/v1/login/token')
async def login_token(request: Request, response: Response):
    """
    Logs in an existing user via JWT authentication

    Args:
        request (Request): request body from the frontend
        response (Response): response object to be returned in the header

    Returns:
        dict: a dictionary containing an error message or a welcome message
    """
    data: Coroutine[Any, Any, Any] = await request.json()
    token: str = data["token"]
    token: Tuple[str, str] = find_token(token)
    if (token is not None):
        try:
            token_decoded = verify_token(token[0], token[1])
            response.status_code = status.HTTP_200_OK
            return { "message": token_decoded["username"] }
        except jwt.ExpiredSignatureError:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return { "message": "Token expired" }
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Token not found" }
        
@app.post("/api/v1/login/credentials")
async def login_credentials(request: Request, response: Response):
    data: Coroutine[Any, Any, Any] = await request.json()
    email: str = data["email"]
    password: str = data["password"]
    user: Tuple[str, str, str] = find_user(email)
    if (user is not None):
        if (password == decrypt_password(user[1], user[2])):
            secret: str = generate_secret()
            today: Any = datetime.today().date() 
            expiry_date: Any = datetime.now(tz=timezone.utc) + timedelta(days=2)
            payload: dict = { "username": user[0], "email": email, "password": user[1], "exp": expiry_date }
            token: str = generate_token(payload, secret)
            insert_new_token(token, secret, today, email)
            response.status_code = status.HTTP_200_OK
            return { "message": f"Welcome {user[0]}", "JWT": token, "Expiry Date": expiry_date }
        else:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return { "message": "Incorrect password" }
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "message": "Email not found" }
    

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", port=8000, reload=True)