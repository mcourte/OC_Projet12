import os
import json
import jwt
from datetime import datetime, timedelta, timezone
from config import Base


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
    takes a dictionary user as an argument and serializes it
    in a file called 'session.json'
    """
    with open('session.json', 'w') as f:
        json.dump(token, f, indent=4)


def load_session():
    """
    Open file 'session.json' and read data.
    :raise if no file found return None
    """
    try:
        with open('session.json', 'r') as f:
            session_data = json.load(f)
            return session_data
    except FileNotFoundError:
        return None


def stop_session():
    """
    delete file 'session.json'
    """
    try:
        os.remove('session.json')
    except OSError:
        pass


def read_role():
    """ read role code from the session token
    return None if can't read data
    """
    try:
        token = load_session()
        if token:
            env = Base()
            user_info = jwt.decode(
                            token, env.SECRET_KEY, algorithms=['HS256'])
            return user_info['role']
        else:
            return None
    except Exception:
        return None
