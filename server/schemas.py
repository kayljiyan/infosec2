from uuid import UUID
from pydantic import BaseModel, EmailStr
from datetime import datetime

class User(BaseModel):
    """
    A user object

    Args:
        user_name (str): the user's name
        user_email (EmailStr): the user's email
    """
    user_uuid: str
    user_name: str
    user_email: EmailStr
    
class UserInDB(User):
    """
    A user object
    
    Args:
        hashed_password (str): the user's hashed password
    """
    hashed_password: str
    user_role: str
    
class UserAddToDB(BaseModel):
    """
    A user object
    
    Args:
        user_name (str): the user's name
    """
    user_fname: str
    user_lname: str
    user_password: str
    user_email: EmailStr
    user_role: str
    
class AppointmentAddToDB(BaseModel):
    """
    An appointment object
    
    Args:
        user_uuid (str): the user's uuid
    """
    user_uuid: str
    
class AppointmentUpdateToDB(BaseModel):
    """
    A user object
    
    Args:
        user_name (str): the user's name
    """
    appointment_date: datetime | None = None
    appointment_status: str
    teller_uuid: str
    
class Appointment(BaseModel):
    appointment_uuid: str
    appointment_date: datetime
    appointment_status: str
    user_uuid: str
    teller_uuid: str
    
class RecordAddToDB(BaseModel):
    appointment_uuid: str
    doctor_uuid: str
    
class Record(BaseModel):
    record_uuid: str
    created_date: datetime
    appointment_uuid: str
    doctor_uuid: str
    
class Token(BaseModel):
    """
    A token object

    Args:
        access_token (str): the access token
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    A token object

    Args:
        user_name (str): the user's name
        user_email (str): the user's email
    """
    user_uuid: str | None = None
    user_name: str | None = None
    user_email: str | None = None
    user_role: str | None = None