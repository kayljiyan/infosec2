# modules used
from fastapi import Depends, FastAPI, Request, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import EmailStr
from datetime import datetime, timedelta
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
        print(payload)
        payload = schemas.TokenData(**payload)
        data = payload
        response.status_code = status.HTTP_200_OK
        return { 'data': data }
    except Exception as e:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return { "detail": str(e) }

@app.post('/api/v1/register')
async def register(request: Request, response: Response):
    """
    Signs up a new user

    Args:
        request (Request): request body from the frontend
        response (Response): response object to be returned in the header

    Returns:
        dict: a dictionary containing an error message or the token and expiration date
    """
    data: Coroutine[str, str, str, str, EmailStr, str] = await request.json()
    try:
        user = schemas.UserAddToDB(**data)
        if (security.check_password_strength(user.user_password)):
            user.user_password = security.encrypt_password(user.user_password)
            if (db.check_email_exists(user.user_email)):
                db.insert_new_user(user.user_fname, user.user_lname, user.user_password, user.user_email, user.user_role)
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
        return { "detail": str(e) }

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
    account: schemas.UserInDB | None = db.authenticate_login(request.username, request.password)
    # print(user)
    if (account is not None):
        data = { "user_uuid": account.user_uuid, "user_email": account.user_email, "user_name": account.user_name, "user_role": account.user_role }
        access_token_expiry_date = timedelta(minutes=consts.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.generate_access_token(data, access_token_expiry_date)
        response.status_code = status.HTTP_200_OK
        return schemas.Token(access_token=access_token, token_type="bearer")
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        response.headers["WWW-Authenticate"] = "Bearer"
        return { "detail": "Incorrect email or password" }
    
@app.get("/api/v1/requests")
async def get_requests(token: Annotated[str, Depends(oauth2_scheme)], response: Response):
    try:
        payload = security.verify_access_token(token)
        payload = schemas.TokenData(**payload)
        if payload.user_role == "teller" or payload.user_role == "doctor":
            data = db.get_requests()
            response.status_code = status.HTTP_200_OK
            return { 'data': data }
        else:
            response.status_code = status.HTTP_403_FORBIDDEN
            return { 'detail': "Unauthorized access" }
    except Exception as e:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return { "detail": str(e) }

@app.get("/api/v1/requests/{user_uuid}")
async def get_user_requests(token: Annotated[str, Depends(oauth2_scheme)], user_uuid: str, response: Response):
    try:
        payload = security.verify_access_token(token)
        payload = schemas.TokenData(**payload)
        if payload.user_role == "user" and payload.user_uuid == user_uuid:
            data = db.get_user_requests(user_uuid)
            response.status_code = status.HTTP_200_OK
            return { 'data': data }
        else:
            response.status_code = status.HTTP_403_FORBIDDEN
            return { 'detail': "Unauthorized access" }
    except Exception as e:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return { "detail": str(e) }

@app.get("/api/v1/appointments")
async def get_appointments(token: Annotated[str, Depends(oauth2_scheme)], response: Response):
    try:
        payload = security.verify_access_token(token)
        payload = schemas.TokenData(**payload)
        if payload.user_role == "teller" or payload.user_role == "doctor":
            data = db.get_appointments()
            response.status_code = status.HTTP_200_OK
            return { 'data': data }
        else:
            response.status_code = status.HTTP_403_FORBIDDEN
            return { 'detail': "Unauthorized access" }
    except Exception as e:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return { "detail": str(e) }
    
@app.get("/api/v1/appointments/{user_uuid}")
async def get_user_appointments(token: Annotated[str, Depends(oauth2_scheme)], user_uuid: str, response: Response):
    try:
        payload = security.verify_access_token(token)
        payload = schemas.TokenData(**payload)
        if payload.user_role == "user" and payload.user_uuid == user_uuid:
            data = db.get_user_appointments(user_uuid)
            response.status_code = status.HTTP_200_OK
            return { 'data': data }
        else:
            response.status_code = status.HTTP_403_FORBIDDEN
            return { 'detail': "Unauthorized access" }
    except Exception as e:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return { "detail": str(e) }

@app.get("/api/v1/records")
async def get_records(token: Annotated[str, Depends(oauth2_scheme)], response: Response):
    try:
        payload = security.verify_access_token(token)
        payload = schemas.TokenData(**payload)
        if payload.user_role == "teller" or payload.user_role == "doctor":
            data = db.get_records()
            response.status_code = status.HTTP_200_OK
            return { 'data': data }
        else:
            response.status_code = status.HTTP_403_FORBIDDEN
            return { 'detail': "Unauthorized access" }
    except Exception as e:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return { "detail": str(e) }

@app.post("/api/v1/request")
async def add_request(token: Annotated[str, Depends(oauth2_scheme)], response: Response):
    try:
        payload = security.verify_access_token(token)
        payload = schemas.TokenData(**payload)
        if payload.user_role == "user":
            user_uuid = payload.user_uuid
            db.add_request(user_uuid)
            response.status_code = status.HTTP_201_CREATED
            return { 'detail': "Request sent for approval" }
        else:
            response.status_code = status.HTTP_403_FORBIDDEN
            return { 'detail': "Unauthorized access" }
    except Exception as e:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return { "detail": str(e) }

@app.post("/api/v1/appointment")
async def add_appointment(token: Annotated[str, Depends(oauth2_scheme)], request: Request, response: Response):
    try:
        payload = security.verify_access_token(token)
        payload = schemas.TokenData(**payload)
        if payload.user_role == "teller":
            user_uuid = payload.user_uuid
            data: Coroutine[str, datetime, str] = await request.json()
            query_result = db.add_appointment(data["request_uuid"], data["appointment_date"], data["request_status"], user_uuid)
            if (query_result is None):
                response.status_code = status.HTTP_200_OK
                return { 'detail': "Appointment added" }
            else:
                response.status_code = status.HTTP_404_NOT_FOUND
                return { 'detail': "Request not found" }
        else:
            response.status_code = status.HTTP_403_FORBIDDEN
            return { 'detail': "Unauthorized access" }
    except Exception as e:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return { "detail": str(e) }

@app.post("/api/v1/record")
async def add_record(token: Annotated[str, Depends(oauth2_scheme)], request: Request, response: Response):
    try:
        payload = security.verify_access_token(token)
        payload = schemas.TokenData(**payload)
        if payload.user_role == "doctor":
            user_uuid = payload.user_uuid
            data: Coroutine[str, str] = await request.json()
            db.add_record(data["record_content"], data["appointment_uuid"], user_uuid)
            response.status_code = status.HTTP_201_CREATED
            return { 'detail': "Record has been added" }
        else:
            response.status_code = status.HTTP_403_FORBIDDEN
            return { 'detail': "Unauthorized access" }
    except Exception as e:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return { "detail": str(e) }

@app.delete("/api/v1/request")
async def delete_request(token: Annotated[str, Depends(oauth2_scheme)], request: Request, response: Response):
    try:
        payload = security.verify_access_token(token)
        payload = schemas.TokenData(**payload)
        if payload.user_role == "user":
            user_uuid = payload.user_uuid
            data: Coroutine[str] = await request.json()
            db.cancel_request(user_uuid, data["request_uuid"])
            response.status_code = status.HTTP_200_OK
            return { 'detail': "Request has been deleted" }
        else:
            response.status_code = status.HTTP_403_FORBIDDEN
            return { 'detail': "Unauthorized access" }
    except Exception as e:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return { "detail": str(e) }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", port=8000, reload=True)