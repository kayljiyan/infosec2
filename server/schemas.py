from pydantic import BaseModel, EmailStr

class User(BaseModel):
    """
    A user object

    Args:
        user_name (str): the user's name
        user_email (EmailStr): the user's email
    """
    user_name: str
    user_email: EmailStr
    
class UserInDB(User):
    """
    A user object
    
    Args:
        hashed_password (str): the user's hashed password
    """
    hashed_password: str
    
class UserAddToDB(BaseModel):
    """
    A user object
    
    Args:
        user_name (str): the user's name
    """
    user_fname: str
    user_mname: str
    user_lname: str
    user_password: str
    user_email: EmailStr
    
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
    user_name: str | None = None
    user_email: str | None = None