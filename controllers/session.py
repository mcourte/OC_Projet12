# Import généraux
import sys
import os
import json
import jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import logging

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

# Import Modèles
from models.entities import EpicUser

# Configuration de la session SQLAlchemy
engine = create_engine('postgresql://postgres:password@localhost:5432/app_db')
Session = sessionmaker(bind=engine)
session = Session()

SECRET_KEY = "openclassroom_projet12"
ALGORITHM = "HS256"
SESSION_FILE = 'session.json'
logging.basicConfig(level=logging.DEBUG)


def create_token(user_data, secret=SECRET_KEY):
    """
    Crée un jeton JWT pour l'utilisateur.

    Paramètres :
    ------------
    user_data : dict
        Dictionnaire contenant les informations de l'utilisateur.

    secret : str
        Clé secrète utilisée pour signer le jeton.

    Retourne :
    ----------
    str : Le jeton JWT.
    """
    payload = {
        "username": user_data['username'],
        "role": user_data['role'],
        "exp": datetime.utcnow() + timedelta(minutes=180)  # Par exemple, 30 minutes
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def save_session(token):
    """
    Sauvegarde le jeton de session dans un fichier JSON.
    """
    try:
        session_file_path = os.path.join(os.getcwd(), 'session.json')
        with open(session_file_path, 'w') as f:
            json.dump({'token': token}, f, indent=4)
    except IOError as e:
        print(f"Erreur lors de l'écriture dans le fichier de session : {e}")


def load_session():
    """
    Charge le token de session à partir du fichier JSON.

    Returns:
    -------
    str
        Le token JWT chargé ou None si le fichier n'existe pas ou est invalide.
    """
    try:
        session_file_path = os.path.join(os.getcwd(), 'session.json')
        with open(session_file_path, 'r') as file:
            data = json.load(file)
            token = data.get('token')
            return token
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        print(f"Erreur de décodage JSON : {e}")
        return None


def decode_token(token, secret_key, algorithm):
    """
    Décode le token JWT.

    Parameters:
    ----------
    token : str
        Le token JWT à décoder.
    secret_key : str
        La clé secrète utilisée pour décoder le token.
    algorithm : str
        L'algorithme utilisé pour décoder le token.

    Returns:
    -------
    dict or None
        Les données décodées du token ou None en cas d'erreur.
    """
    try:
        # Tentative de décoder le jeton
        decoded = jwt.decode(token, secret_key, algorithms=[algorithm])
        return decoded
    except jwt.ExpiredSignatureError:
        print("Erreur : Le jeton a expiré.")
        raise PermissionError("Token expired")
    except jwt.InvalidTokenError as e:
        print(f"Erreur : Le jeton est invalide. Détails : {e}")
        raise PermissionError("Token invalid")
    except Exception as e:
        print(f"Erreur inattendue lors du décodage du jeton : {e}")
        raise


def clear_session():
    """
    Supprime le fichier de session pour déconnecter l'utilisateur.
    """
    try:
        os.remove(SESSION_FILE)
        logging.info("Fichier de session supprimé avec succès.")
    except OSError as e:
        logging.error(f"Erreur lors de la suppression du fichier de session : {e}")


def create_session(username, role):
    """
    Crée une session pour l'utilisateur en générant un token JWT et en le sauvegardant.

    Parameters:
    ----------
    username : str
        Le nom d'utilisateur.
    role : str
        Le rôle de l'utilisateur.
    """
    token = create_token(username, role)
    save_session(token)


def renew_session():
    """
    Renouvelle le token JWT stocké dans 'session.json'.

    Returns:
    -------
    str
        Le nouveau token JWT ou None en cas d'erreur.
    """
    user = get_current_user()
    if user is None:
        return None

    new_token = create_token(user.username, user.role)
    save_session(new_token)
    return new_token


def get_current_user():
    """
    Récupère l'utilisateur actuellement connecté à partir du token JWT stocké.

    Returns:
    -------
    EpicUser
        L'utilisateur connecté ou None si aucun utilisateur n'est trouvé.
    """
    token = load_session()
    if not token:
        logging.error("Erreur : Aucun jeton trouvé dans la session.")
        return None

    try:
        decoded = decode_token(token, SECRET_KEY, ALGORITHM)
    except PermissionError:
        # Si le jeton a expiré, on le renouvelle
        logging.info("Le jeton a expiré. Tentative de renouvellement...")
        new_token = force_refresh_token()
        if new_token:
            decoded = decode_token(new_token, SECRET_KEY, ALGORITHM)
        else:
            return None

    username = decoded.get('username')
    if not username:
        logging.error("Erreur : Le jeton ne contient pas d'identifiant d'utilisateur.")
        return None

    user = session.query(EpicUser).filter_by(username=username).first()
    if not user:
        logging.error(f"Utilisateur {username} non trouvé dans la base de données.")
        return None

    return user


def force_refresh_token():
    """
    Force le renouvellement du token JWT en le recréant avec les mêmes informations utilisateur.

    Returns:
    -------
    str
        Le nouveau token JWT ou None en cas d'erreur.
    """
    token = load_session()
    if not token:
        logging.warning("Aucun jeton trouvé dans la session.")
        return None

    try:
        # Tente de décoder le token même s'il est expiré, sans lever une erreur
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
    except jwt.InvalidTokenError as e:
        logging.error(f"Erreur lors du décodage du jeton expiré : {e}")
        return None

    username = decoded.get('username')
    if not username:
        logging.error("Le jeton ne contient pas d'identifiant d'utilisateur.")
        return None

    user = session.query(EpicUser).filter_by(username=username).first()
    if not user:
        logging.error(f"Utilisateur {username} non trouvé dans la base de données.")
        return None

    # Renouvelle le token
    new_token = create_token(serialize_user(user))
    save_session(new_token)
    return new_token


def serialize_user(user):
    """
    Convertit un objet utilisateur en un dictionnaire sérialisable en JSON.
    """
    try:
        return {
            'username': user.username,
            'role': user.role.code if hasattr(user.role, 'code') else str(user.role),
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'state': user.state.code if hasattr(user.state, 'code') else str(user.state)
        }
    except AttributeError as e:
        print(f"Erreur lors de la sérialisation : {e}")
        raise ValueError("L'objet utilisateur n'a pas les attributs requis.")
