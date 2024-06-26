# modules used
from fastapi import Depends, FastAPI, Request, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Any, Coroutine, Annotated, List
import security, db, consts, schemas

# creates the FastAPI app object
app: FastAPI = FastAPI()

# OAuth2PasswordBearer instance
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/login")

@app.get('/')
async def index(token: Annotated[str, Depends(oauth2_scheme)], response: Response):
    """
    Index page for the API

    Args:
        response (Response): response object to be returned in the header

    Returns:
        dict: hello world message
    """
    try:
        payload = security.verify_access_token(token)
        payload = schemas.TokenData(**payload)
        username = payload.user_name
        response.status_code = status.HTTP_200_OK
        return { 'message': f"Welcome {username}" }
    except Exception as e:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return { "detail": str(e) }

@app.post('/api/v1/register')
async def signup(request: Request, response: Response):
    """
    Signs up a new user

    Args:
        request (Request): request body from the frontend
        response (Response): response object to be returned in the header

    Returns:
        dict: a dictionary containing an error message or the token and expiration date
    """
    data: Coroutine[str, str, str, str, str] = await request.json()
    try:
        user = schemas.UserAddToDB(**data)
        if (security.check_password_strength(user.user_password)):
            user.user_password = security.encrypt_password(user.user_password)
            if (db.check_email_exists(user.user_email)):
                db.insert_new_user(user.user_fname, user.user_mname, user.user_lname, user.user_password, user.user_email)
                response.status_code = status.HTTP_201_CREATED
                return { "detail": "User created" }
            else:
                response.status_code = status.HTTP_400_BAD_REQUEST
                return { "detail": "Email already exists" }
        else:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return { "detail": "Password is too weak" }
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "detail": "Invalid email address" }

@app.post('/api/v1/login')
async def login(
    request: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response
    ):
    """
    Logs in a user

    Args:
        request (OAuth2PasswordRequestForm): request body from the frontend
        response (Response): response object to be returned in the header

    Returns:
        models.Token: a dictionary containing the access token and expiration date
    """
    user: schemas.UserInDB | None = db.authenticate_user(request.username, request.password)
    # print(user)
    if (user is not None):
        data = {"user_email": user.user_email, "user_name": user.user_name}
        access_token_expiry_date = timedelta(minutes=consts.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.generate_access_token(data, access_token_expiry_date)
        response.status_code = status.HTTP_200_OK
        return schemas.Token(access_token=access_token, token_type="bearer")
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        response.headers["WWW-Authenticate"] = "Bearer"
        return { "detail": "Incorrect username or password" }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", port=8000, reload=True)