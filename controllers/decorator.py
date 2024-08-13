import jwt
from .session import load_session, read_role
from config import SECRET_KEY


def is_authenticated(f):
    def decorator(*args, **kwargs):
        token = load_session()
        try:
            jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return "Token Expiré"
        except jwt.InvalidTokenError:
            return "Token Invalid"
    return decorator


def is_commercial(f):
    def decorator(*args, **kwargs):
        role_code = read_role()
        if role_code == 'COM':
            return f(*args, **kwargs)
        else:
            return "Vous n'avez pas les autorisations nécessaire pour effectuer cette action"
    return decorator


def is_support(f):
    def decorator(*args, **kwargs):
        role_code = read_role()
        if role_code == 'SUP':
            return f(*args, **kwargs)
        else:
            return "Vous n'avez pas les autorisations nécessaire pour effectuer cette action"
    return decorator


def is_gestion(f):
    def decorator(*args, **kwargs):
        role_code = read_role()
        if role_code == 'GES':
            return f(*args, **kwargs)
        else:
            return "Vous n'avez pas les autorisations nécessaire pour effectuer cette action"
    return decorator


def is_admin(f):
    def decorator(*args, **kwargs):
        role_code = read_role()
        if role_code == 'ADM':
            return f(*args, **kwargs)
        else:
            return "Vous n'avez pas les autorisations nécessaire pour effectuer cette action"
    return decorator
