# modules used
from dotenv import load_dotenv
import os

# loads the environment variables
load_dotenv()

# environment variables
POSTGRES_DATABASE: str = os.environ.get('POSTGRES_DATABASE')
POSTGRES_HOST: str = os.environ.get('POSTGRES_HOST')
POSTGRES_USER: str = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD: str = os.environ.get('POSTGRES_PASSWORD')
POSTGRES_PORT: str = os.environ.get('POSTGRES_PORT')
SECRET_KEY: str = os.environ.get('SECRET_KEY')
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30