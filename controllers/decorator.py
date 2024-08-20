import jwt
from functools import wraps
from .session import load_session, read_role
from config import SECRET_KEY
from jwt.exceptions import DecodeError


def is_authenticated(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = load_session()
        try:
            jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            raise PermissionError("Token Expiré")
        except jwt.InvalidTokenError:
            raise PermissionError("Token Invalid")
    return decorator


def is_commercial(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        role_code = read_role()
        if role_code in {'COM', 'ADM', 'Commercial', 'Admin'}:
            return f(*args, **kwargs)
        else:
            print(f"PermissionError: User role is {role_code}, required 'Commercial' or 'COM'")
            raise PermissionError("Vous n'avez pas les autorisations nécessaires pour effectuer cette action")
    return decorator


def is_support(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        role_code = read_role()
        if role_code in {'SUP', 'ADM', 'Support', 'Admin'}:
            return f(*args, **kwargs)
        else:
            print(f"PermissionError: User role is {role_code}, required 'Support' or 'SUP'")
            raise PermissionError("Vous n'avez pas les autorisations nécessaires pour effectuer cette action")
    return decorator


def is_gestion(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        role_code = read_role()
        if role_code in {'GES', 'ADM', 'Gestion', 'Admin'}:
            return f(*args, **kwargs)
        else:
            print(f"PermissionError: User role is {role_code}, required 'Gestion' or 'GES'")
            raise PermissionError("Vous n'avez pas les autorisations nécessaires pour effectuer cette action")
    return decorator


def is_admin(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        role_code = read_role()
        if role_code in {'ADM', 'Admin'}:
            return f(*args, **kwargs)
        else:
            print(f"PermissionError: User role is {role_code}, required 'Admin' or 'ADM'")
            raise PermissionError("Vous n'avez pas les autorisations nécessaires pour effectuer cette action")
    return decorator


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = load_session()
        if not token:
            raise ValueError("Token not found")
        try:
            # Assurez-vous que le token est une chaîne
            if isinstance(token, str):
                decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            else:
                raise ValueError("Token must be a string")

            # Pass decoded data to the function or handle as needed
            return f(decoded, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
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
