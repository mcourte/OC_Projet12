import os
import json
import jwt
from datetime import datetime, timedelta, timezone
from config import SECRET_KEY


def create_session(e, delta, secret):
    data = {
        'username': e.username,
        'exp': datetime.now(tz=timezone.utc) + timedelta(seconds=delta),
        'role': e.role.code
    }
    token = jwt.encode(data, secret, algorithm='HS256')
    save_session(token)


def save_session(token):
    """
    Save the JWT token to 'session.json'.
    """
    with open('session.json', 'w') as f:
        json.dump({'token': token}, f, indent=4)


def load_session():
    """
    Load the JWT token from 'session.json'.
    :return: JWT token as a string or None if file not found or invalid.
    """
    try:
        with open('session.json', 'r') as f:
            data = json.load(f)
            token = data.get('token')
            return token
    except FileNotFoundError:
        print("File not found.")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return None


def stop_session():
    """
    Delete 'session.json' file to stop the session.
    """
    try:
        os.remove('session.json')
    except OSError:
        pass


def read_role():
    token = load_session()
    if not token:
        return None
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        role = decoded.get('role')
        return role
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
