from pydantic import BaseModel

class User(BaseModel):
    """
    User model

    Args:
        BaseModel (pydantic.BaseModel): base model class
    """
    email: str
    username: str
    password: str