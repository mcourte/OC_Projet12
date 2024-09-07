# Import généraux
import jwt
from functools import wraps
from controllers.session import load_session, decode_token
from jwt.exceptions import DecodeError
import sys
import os
import sentry_sdk
from sentry_sdk import capture_exception

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)


# Import des Controllers
from controllers.session import ALGORITHM, SECRET_KEY

# Import des Modèles
from models.entities import EpicUser


def sentry_activate(f):
    """
    Décorateur pour activer Sentry pour la gestion des exceptions.

    Ce décorateur démarre une transaction Sentry pour capturer les exceptions
    et les signaler à Sentry pour une surveillance et une gestion appropriées.

    Paramètres :
    ------------
    f : fonction
        La fonction à décorer.

    Retourne :
    ----------
    fonction
        La fonction décorée avec gestion des exceptions Sentry.
    """
    def decorator(*args, **kwargs):
        with sentry_sdk.start_transaction(name="epicevent"):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                # Affichage de l'erreur localement
                print(f"Erreur inattendue : {str(e)}")
                # Capture l'exception dans Sentry
                capture_exception(e)
                raise  # Relance l'exception après capture
    return decorator


def is_commercial(f):
    """
    Décorateur pour vérifier si l'utilisateur a un rôle commercial.

    Ce décorateur vérifie si l'utilisateur a un rôle correspondant à
    'COM', 'ADM', 'Commercial', ou 'Admin'. S'il ne correspond pas,
    une exception `PermissionError` est levée.

    Paramètres :
    ------------
    f : fonction
        La fonction à décorer.

    Retourne :
    ----------
    fonction
        La fonction décorée avec vérification du rôle commercial.
    """
    @wraps(f)
    def decorator(*args, **kwargs):
        try:
            role_code = decode_token(load_session(), SECRET_KEY, ALGORITHM).get('role')
            print(f"Rôle de l'utilisateur : {role_code}")  # Débogage
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
    """
    Décorateur pour vérifier si l'utilisateur a un rôle de support.

    Ce décorateur vérifie si l'utilisateur a un rôle correspondant à
    'SUP', 'ADM', 'Support', ou 'Admin'. S'il ne correspond pas,
    une exception `PermissionError` est levée.

    Paramètres :
    ------------
    f : fonction
        La fonction à décorer.

    Retourne :
    ----------
    fonction
        La fonction décorée avec vérification du rôle de support.
    """
    @wraps(f)
    def decorator(*args, **kwargs):
        try:
            role_code = decode_token(load_session(), SECRET_KEY, ALGORITHM).get('role')
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
    """
    Décorateur pour vérifier l'authentification d'un utilisateur.

    Ce décorateur vérifie si l'utilisateur est authentifié en vérifiant la présence
    et la validité d'un jeton dans la session. Il valide également que l'utilisateur
    est actif et définit `self.current_user`.

    Paramètres :
    ------------
    f : fonction
        La fonction à décorer.

    Retourne :
    ----------
    fonction
        La fonction décorée avec vérification de l'authentification.
    """
    @wraps(f)
    def decorator(cls, session, *args, **kwargs):
        token = load_session()
        if not token:
            print("Erreur : Aucun jeton trouvé dans la session.")
            raise PermissionError("Token not found")

        try:
            decoded = decode_token(token, SECRET_KEY, ALGORITHM)
            if not decoded or 'username' not in decoded:
                print("Erreur : Le jeton est invalide ou incomplet.")
                raise PermissionError("Token invalid")

            # Cherchez l'utilisateur dans la base de données
            user = session.query(EpicUser).filter_by(username=decoded['username']).one_or_none()
            if user is None:
                print(f"Erreur : Utilisateur {decoded['username']} non trouvé.")
                raise PermissionError("User not found")

            if user.state != 'A':
                print("Erreur : Utilisateur inactif.")
                raise PermissionError("User inactive")
            # Assurez-vous de définir self.current_user
            cls.current_user = user
            return f(cls, session, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            print("Erreur : Le jeton a expiré.")
            raise PermissionError("Token expired")
        except jwt.InvalidTokenError as e:
            print(f"Erreur : {e}")
            raise PermissionError("Token invalid")
        except PermissionError as e:
            print(f"Erreur de permission : {e}")
            raise
        except Exception as e:
            print(f"Erreur inattendue : {e}")
            raise
    return decorator


def is_admin(f):
    """
    Décorateur pour vérifier si l'utilisateur a des privilèges d'administrateur.

    Ce décorateur vérifie si l'utilisateur a un rôle correspondant à
    'ADM' ou 'Admin'. S'il ne correspond pas, une exception `PermissionError` est levée.

    Paramètres :
    ------------
    f : fonction
        La fonction à décorer.

    Retourne :
    ----------
    fonction
        La fonction décorée avec vérification des privilèges d'administrateur.
    """
    @wraps(f)
    def decorator(cls, session, *args, **kwargs):
        token = load_session()
        if token is None:
            raise PermissionError("Token not found")
        try:
            decoded = decode_token(token, SECRET_KEY, ALGORITHM)
            if decoded.get('role') in {'ADM', 'Admin'}:
                print("Inside is_authenticated decorator")
                print(f"Arguments passed: {args}, {kwargs}")
                return f(cls, session, *args, **kwargs)
            else:
                raise PermissionError("User does not have admin permissions")
        except PermissionError as e:
            print(e)
            raise

    return decorator


def is_gestion(f):
    """
    Décorateur pour vérifier si l'utilisateur a des privilèges de gestion.

    Ce décorateur vérifie si l'utilisateur a un rôle correspondant à
    'GES', 'ADM', 'Gestion', ou 'Admin'. S'il ne correspond pas,
    une exception `PermissionError` est levée.

    Paramètres :
    ------------
    f : fonction
        La fonction à décorer.

    Retourne :
    ----------
    fonction
        La fonction décorée avec vérification des privilèges de gestion.
    """
    @wraps(f)
    def decorator(cls, session, *args, **kwargs):
        token = load_session()
        if token is None:
            raise PermissionError("Token not found")
        try:
            decoded = decode_token(token, SECRET_KEY, ALGORITHM)
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

    Ce décorateur vérifie si l'utilisateur a un rôle correspondant à l'un
    des rôles spécifiés. S'il ne correspond pas, une exception `PermissionError` est levée.

    Paramètres :
    ------------
    *roles : str
        Les rôles requis pour accéder à la fonction.

    Retourne :
    ----------
    fonction
        La fonction décorée avec vérification des rôles requis.
    """
    def decorator(f):
        @wraps(f)
        def wrapped(cls, session, *args, **kwargs):
            token = load_session()
            if not token:
                raise PermissionError("Token not found")

            try:
                decoded = decode_token(token, SECRET_KEY, ALGORITHM)
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
    """
    Décorateur pour vérifier la présence d'un jeton dans la session.

    Ce décorateur vérifie que le jeton est présent dans la session, puis le décode
    pour le passer à la fonction décorée.

    Paramètres :
    ------------
    f : fonction
        La fonction à décorer.

    Retourne :
    ----------
    fonction
        La fonction décorée avec vérification de la présence du jeton.
    """
    @wraps(f)
    def decorator(*args, **kwargs):
        token = load_session()
        if not token:
            raise ValueError("Token not found")
        try:
            decoded = decode_token(token, SECRET_KEY, ALGORITHM)
            return f(decoded, *args, **kwargs)
        except PermissionError as e:
            print(e)
            raise
    return decorator


def decorator(f):
    """
    Décorateur générique pour vérifier les permissions de l'utilisateur.

    Ce décorateur vérifie la présence et la validité du jeton, et s'assure que
    l'utilisateur a l'un des rôles autorisés pour effectuer l'action demandée.

    Paramètres :
    ------------
    f : fonction
        La fonction à décorer.

    Retourne :
    ----------
    fonction
        La fonction décorée avec vérification des permissions de l'utilisateur.
    """
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
            decoded_token = decode_token(token, SECRET_KEY, ALGORITHM)

            # Vérification des permissions ici
            if decoded_token.get('role') not in ['ADM', 'GES', 'SUP', 'COM']:
                raise PermissionError("Vous n'avez pas les autorisations nécessaires pour effectuer cette action")

            return f(*args, **kwargs)

        except DecodeError:
            raise PermissionError("Token Invalid")
        except Exception as e:
            raise e
    return wrapper
