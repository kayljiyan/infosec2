# modules used
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Tuple
from security import verify_password
from psycopg2.extras import register_uuid
from uuid import UUID
import os, psycopg2, schemas

register_uuid()

user_structure = [ "user_uuid", "user_name", "user_email", "hashed_password", "user_role" ]
request_structure = [ "request_uuid", "request_status", "created_at" ]

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


def insert_new_user(fname: str, lname: str, password: str, email: str, role: str) -> None:
    """
    Inserts a new user into the users table

    Args:
        fname (str): user first name
        lname (str): user last name
        password (str): user password
        email (str): user email
        role (str): user role
    """
    with conn.cursor() as cur:
        cur.execute("INSERT INTO users (user_fname, user_lname, user_password, user_email, user_role) VALUES (%s,%s,%s,%s,%s)",
                        (fname,
                        lname,
                        password,
                        email,
                        role))
    conn.commit()

def check_email_exists(email: str) -> bool:
    """
    Checks if an email already exists in the users table

    Args:
        email (str): user email

    Returns:
        bool: True if the email exists, False otherwise
    """
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE user_email=(%s)", (email,))
        return cur.fetchone() is None

def get_account(email: str) -> schemas.UserInDB | None:
    """
    Retrieves user data from the users table

    Args:
        email (str): user email

    Returns:
        schemas.UserInDB | None: user data if found, None otherwise
    """
    with conn.cursor() as cur:
        cur.execute("SELECT user_uuid, CONCAT(user_lname, ', ', user_fname) AS user_name, user_email, user_password, user_role FROM users WHERE user_email=(%s)", (email,))
        user = cur.fetchone()
        if user is not None:
            user_dict = { user_structure[i] : str(user[i]) for i, _ in enumerate(user) }
            return schemas.UserInDB(**user_dict)
        else:
            return None
    
def authenticate_login(email: str, password: str):
    """
    Authenticates a user based on their email and password

    Args:
        email (str): user email
        password (str): user password
    """
    account = get_account(email)
    # print(account)
    if not account:
        return None
    if not verify_password(password, account.hashed_password):
        return None
    return account

def add_request(user_uuid: str):
    """
    Adds a new request to the requests table

    Args:
        user_uuid (str): user uuid
    """
    user_uuid: UUID = UUID(user_uuid)
    with conn.cursor() as cur:
        cur.execute("INSERT INTO requests (user_uuid) VALUES (%s)", (user_uuid,))
    conn.commit()

def add_appointment(request_uuid: str, appointment_date: str, request_status: str, user_uuid: str) -> Exception | None:
    """
    Adds a new appointment to the appointments table

    Args:
        request_uuid (str): request uuid
        appointment_date (str): appointment date
        request_status (str): request status
        user_uuid (str): user uuid

    Returns:
        Exception | None: None if the appointment is added successfully, Exception otherwise
    """
    user_uuid: UUID = UUID(user_uuid)
    request_uuid: UUID = UUID(request_uuid)
    appointment_date: datetime = datetime.strptime(appointment_date, '%m/%d/%y %H:%M:%S')
    with conn.cursor() as cur:
        try:
            cur.execute("UPDATE requests SET request_status = (%s) WHERE request_uuid = (%s)", (request_status, request_uuid))
            cur.execute("INSERT INTO appointments (appointment_date, user_uuid, request_uuid) VALUES (%s, %s, %s)", (appointment_date, user_uuid, request_uuid))
        except Exception:
            return Exception
    conn.commit()

def add_record(record_content: str, appointment_uuid: str, user_uuid: str):
    """
    Adds a new record to the records table

    Args:
        record_content (str): record content
        appointment_uuid (str): appointment uuid
        user_uuid (str): user uuid
    """
    appointment_uuid: UUID = UUID(appointment_uuid)
    user_uuid: UUID = UUID(user_uuid)
    with conn.cursor() as cur:
        cur.execute("INSERT INTO records (record_content, user_uuid, appointment_uuid) VALUES (%s, %s, %s)", (record_content, user_uuid, appointment_uuid))
    conn.commit()
    
def cancel_request(user_uuid: str, request_uuid: str):
    """
    Cancels a request based on the user uuid and request uuid

    Args:
        user_uuid (str): user uuid
    """
    request_uuid: UUID = UUID(request_uuid)
    user_uuid: UUID = UUID(user_uuid)
    with conn.cursor() as cur:
        cur.execute("DELETE FROM requests WHERE request_uuid = (%s) AND user_uuid = (%s)", (request_uuid, user_uuid))
    conn.commit()
    
def get_requests() -> List[Tuple[UUID, str, datetime]] | None:
    """
    Retrieves all requests from the requests table

    Returns:
        List[Tuple[UUID, str, datetime]] | None: requests if found, None otherwise
    """
    with conn.cursor() as cur:
        cur.execute("SELECT request_uuid, request_status, created_at FROM requests")
        return cur.fetchall()

def get_user_requests(user_uuid) -> List[Tuple[UUID, str, datetime]] | None:
    """
    Retrieves all requests for a specific user from the requests table

    Args:
        user_uuid (str): user uuid

    Returns:
        List[Tuple[UUID, str, datetime]] | None: requests if found, None otherwise
    """
    with conn.cursor() as cur:
        cur.execute("SELECT request_uuid, request_status, created_at FROM requests WHERE user_uuid=(%s)", (user_uuid,))
        requests = cur.fetchall()
        request_list = []
        for request in requests:
            request_list.append(
                { request_structure[i] : str(request[i]) for i, _ in enumerate(request)}
            )
        return request_list

def get_appointments() -> List[Tuple[UUID, str, datetime]] | None:
    """
    Retrieves all appointments from the appointments table

    Returns:
        List[Tuple[UUID, str, datetime]] | None: appointments if found, None otherwise
    """
    with conn.cursor() as cur:
        cur.execute("SELECT appointment_uuid, CONCAT(user_lname, ', ', user_fname) AS user_name, appointment_date  FROM appointments INNER JOIN users ON appointments.user_uuid = users.user_uuid")
        return cur.fetchall()

def get_user_appointments(user_uuid) -> List[Tuple[UUID, str, datetime]] | None:
    """
    Retrieves all appointments for a specific user from the appointments table

    Args:
        user_uuid (str): user uuid
        
    Returns:
    List[Tuple[UUID, str, datetime]] | None: appointments if found, None otherwise
    """
    with conn.cursor() as cur:
        cur.execute("SELECT appointment_uuid, appointment_date FROM appointments INNER JOIN requests ON appointments.request_uuid = requests.request_uuid WHERE requests.user_uuid=(%s)", (user_uuid,))
        return cur.fetchall()

def get_records() -> List[Tuple[UUID, str, str, datetime]] | None:
    """
    Retrieves all records from the records table

    Returns:
        List[Tuple[UUID, str, str, datetime]] | None: records if found, None otherwise
    """
    with conn.cursor() as cur:
        cur.execute("SELECT record_uuid, record_content, CONCAT(user_lname, ', ', user_fname) AS user_name, appointment_date FROM appointments INNER JOIN users INNER JOIN records ON records.user_uuid = users.user_uuid ON records.appointment_uuid = appointments.appointment_uuid")
        return cur.fetchall()
    
def change_password(email: str, password: str):
    """
    Changes the password for a user based on their email

    Args:
        email (str): user email
        password (str): new password
    """
    with conn.cursor() as cur:
        cur.execute("UPDATE users SET user_password = (%s) WHERE user_email = (%s)", (password, email))