# modules used
from datetime import datetime
from dotenv import load_dotenv
from typing import Any
from security import verify_password
from psycopg2.extras import register_uuid
from uuid import UUID
import os, psycopg2, schemas

register_uuid()

user_structure = [ "user_uuid", "user_name", "user_email", "hashed_password" ]

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


def insert_new_user(fname: str, mname: str, lname: str, password: str, email: str, role: str) -> None:
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
        match role:
            case "doctor":
                cur.execute("INSERT INTO doctors (doctor_fname, doctor_mname, doctor_lname, doctor_password, doctor_email) VALUES (%s,%s,%s,%s,%s)",
                        (fname,
                        mname,
                        lname,
                        password,
                        email))
            case "teller":
                cur.execute("INSERT INTO tellers (teller_fname, teller_mname, teller_lname, teller_password, teller_email) VALUES (%s,%s,%s,%s,%s)",
                        (fname,
                        mname,
                        lname,
                        password,
                        email))
            case "user":
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
        cur.execute("SELECT * FROM doctors WHERE doctor_email=(%s)", (email,))
        if cur.fetchone() is not None:
            return True
        cur.execute("SELECT * FROM tellers WHERE teller_email=(%s)", (email,))
        if cur.fetchone() is not None:
            return True
        cur.execute("SELECT * FROM users WHERE user_email=(%s)", (email,))
        if cur.fetchone() is not None:
            return True
        return False

def get_account(email: str) -> schemas.UserInDB | None:
    """
    Gets a user from the users table

    Args:
        email (str): user email

    Returns:
        Tuple[str, str, str] | None: a tuple containing the user's name, and email if the email exists, None otherwise
    """
    with conn.cursor() as cur:
        cur.execute("SELECT doctor_uuid, CONCAT(doctor_lname, ', ', doctor_fname, ' ', doctor_mname) AS doctor_name, doctor_email, doctor_password FROM doctors WHERE doctor_email=(%s)", (email,))
        doctor = cur.fetchone()
        if doctor is not None:
            doctor_dict = { user_structure[i] : str(doctor[i]) for i, _ in enumerate(doctor) }
            doctor_dict.update({"role": "doctor"})
            return schemas.UserInDB(**doctor_dict)
        cur.execute("SELECT teller_uuid, CONCAT(teller_lname, ', ', teller_fname, ' ', teller_mname) AS teller_name, teller_email, teller_password FROM tellers WHERE teller_email=(%s)", (email,))
        teller = cur.fetchone()
        if teller is not None:
            teller_dict = { user_structure[i] : str(teller[i]) for i, _ in enumerate(teller) }
            teller_dict.update({"role": "teller"})
            return schemas.UserInDB(**teller_dict)
        cur.execute("SELECT user_uuid, CONCAT(user_lname, ', ', user_fname, ' ', user_mname) AS user_name, user_email, user_password FROM users WHERE user_email=(%s)", (email,))
        user = cur.fetchone()
        if user is not None:
            user_dict = { user_structure[i] : str(user[i]) for i, _ in enumerate(user) }
            user_dict.update({"role": "user"})
            return schemas.UserInDB(**user_dict)
        else:
            return None
    
def authenticate_login(email: str, password: str):
    """
    Authenticates an account

    Args:
        email (str): account email
    """
    account = get_account(email)
    # print(account)
    if not account:
        return None
    if not verify_password(password, account.hashed_password):
        return None
    return account

def add_appointment(user_uuid: str):
    user_uuid: UUID = UUID(user_uuid)
    with conn.cursor() as cur:
        cur.execute("INSERT INTO appointments (user_uuid) VALUES (%s)", (user_uuid,))
    conn.commit()

def update_appointment(appointment_uuid: str, appointment_date: str, appointment_status: str, teller_uuid: str) -> Exception | None:
    teller_uuid: UUID = UUID(teller_uuid)
    appointment_uuid: UUID = UUID(appointment_uuid)
    appointment_date: datetime = datetime.strptime(appointment_date, '%m/%d/%y %H:%M:%S')
    with conn.cursor() as cur:
        try:
            cur.execute("UPDATE appointments SET appointment_date = (%s), appointment_status = (%s), teller_uuid = (%s) WHERE appointment_uuid = (%s)", (appointment_date, appointment_status, teller_uuid, appointment_uuid))
        except Exception:
            return Exception
    conn.commit()

def add_record(appointment_uuid: str, doctor_uuid: str):
    appointment_uuid: UUID = UUID(appointment_uuid)
    doctor_uuid: UUID = UUID(doctor_uuid)
    with conn.cursor() as cur:
        cur.execute("INSERT INTO records (appointment_uuid, doctor_uuid) VALUES (%s, %s)", (appointment_uuid, doctor_uuid))
    conn.commit()
    
def delete_appointment(user_uuid: str, appointment_uuid: str):
    appointment_uuid: UUID = UUID(appointment_uuid)
    user_uuid: UUID = UUID(user_uuid)
    with conn.cursor() as cur:
        cur.execute("DELETE FROM appointments WHERE appointment_uuid = (%s) AND user_uuid = (%s)", (appointment_uuid, user_uuid))
    conn.commit()