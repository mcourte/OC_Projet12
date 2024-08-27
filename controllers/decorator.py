import jwt
from functools import wraps
from controllers.session import load_session, decode_token
from jwt.exceptions import DecodeError
import sys
import os

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from config_init import SECRET_KEY


def is_commercial(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        try:
            role_code = decode_token(load_session(), SECRET_KEY).get('role')
            print(f"Rôle de l'utilisateur : {role_code}")  # Debugging
            if role_code in {'COM', 'ADM', 'Commercial', 'Admin'}:
                return f(*args, **kwargs)
            else:
                print(f"PermissionError: User role is {role_code}, required 'Commercial' or 'COM'")
                raise PermissionError("Vous n'avez pas les autorisations nécessaires pour effectuer cette action")
        except PermissionError as e:
            print(e)
            raise
    return decorator


def is_support(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        try:
            role_code = decode_token(load_session(), SECRET_KEY).get('role')
            if role_code in {'SUP', 'ADM', 'Support', 'Admin'}:
                return f(*args, **kwargs)
            else:
                print(f"PermissionError: User role is {role_code}, required 'Support' or 'SUP'")
                raise PermissionError("Vous n'avez pas les autorisations nécessaires pour effectuer cette action")
        except PermissionError as e:
            print(e)
            raise
    return decorator


def is_authenticated(f):
    @wraps(f)
    def decorator(cls, session, *args, **kwargs):
        token = load_session()
        if token is None:
            raise PermissionError("Token not found")
        try:
            decoded = decode_token(token, SECRET_KEY)
            if decoded:
                return f(cls, session, *args, **kwargs)
            else:
                raise PermissionError("Token invalid")
        except PermissionError as e:
            print(e)
            raise
    return decorator


def is_admin(f):
    @wraps(f)
    def decorator(cls, session, *args, **kwargs):
        token = load_session()
        if token is None:
            raise PermissionError("Token not found")
        try:
            decoded = decode_token(token, SECRET_KEY)
            if decoded.get('role') in {'ADM', 'Admin'}:
                return f(cls, session, *args, **kwargs)
            else:
                raise PermissionError("User does not have admin permissions")
        except PermissionError as e:
            print(e)
            raise
    return decorator


def is_gestion(f):
    @wraps(f)
    def decorator(cls, session, *args, **kwargs):
        token = load_session()
        if token is None:
            raise PermissionError("Token not found")
        try:
            decoded = decode_token(token, SECRET_KEY)
            if decoded.get('role') in {'GES', 'ADM', 'Gestion', 'Admin'}:
                return f(cls, session, *args, **kwargs)
            else:
                raise PermissionError("User does not have gestion permissions")
        except PermissionError as e:
            print(e)
            raise
    return decorator


def requires_roles(*roles):
    """
    Décorateur pour vérifier si l'utilisateur a l'un des rôles requis.
    """
    def decorator(f):
        @wraps(f)
        def wrapped(cls, session, *args, **kwargs):
            token = load_session()
            if token is None:
                raise PermissionError("Token not found")

            try:
                decoded = decode_token(token, SECRET_KEY)
                user_role = decoded.get('role')
                if user_role not in roles:
                    raise PermissionError(f"PermissionError: User role is {user_role}, required one of {roles}")
                return f(cls, session, *args, **kwargs)
            except PermissionError as e:
                print(e)
                raise
        return wrapped
    return decorator


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = load_session()
        if not token:
            raise ValueError("Token not found")
        try:
            decoded = decode_token(token, SECRET_KEY)
            return f(decoded, *args, **kwargs)
        except PermissionError as e:
            print(e)
            raise
    return decorator


def decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            # Charger le jeton depuis la session
            token = load_session()
            if not token:
                raise ValueError("No token found in session")

            # Assurez-vous que le token est une chaîne et non pas None
            if not isinstance(token, str):
                raise ValueError("Token must be a string")

            # Décoder le token en utilisant jwt.decode
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

            # Vérification des permissions ici
            if decoded_token.get('role') not in ['ADM', 'GES', 'SUP', 'COM']:
                raise PermissionError("Vous n'avez pas les autorisations nécessaires pour effectuer cette action")

            return f(*args, **kwargs)

        except DecodeError:
            raise PermissionError("Token Invalid")
        except Exception as e:
            raise e
    return wrapper
