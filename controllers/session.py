import os
import sys
import json
import jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import logging
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from models.entities import EpicUser
from views.console_view import console
# Configuration de la session SQLAlchemy
engine = create_engine('postgresql://postgres:password@localhost:5432/app_db')
Session = sessionmaker(bind=engine)
session = Session()

SECRET_KEY = 'openclassroom_projet12'
ALGORITHM = 'HS256'
logging.basicConfig(level=logging.DEBUG)


def create_token(user, secret=SECRET_KEY):
    """
    Crée un jeton JWT pour un utilisateur avec son rôle.
    """
    if not hasattr(user, 'role') or not user.role:
        raise ValueError("Le rôle de l'utilisateur ne peut pas être None")

    role_value = user.role.code if hasattr(user.role, 'code') else str(user.role)

    payload = {
        'username': user.username,
        'role': role_value,
        'exp': datetime.now(timezone.utc) + timedelta(hours=4)
    }
    token = jwt.encode(payload, secret, algorithm='HS256')
    return token


def decode_token(token, secret_key):
    try:
        if isinstance(token, str):
            token = token.encode('utf-8')
        logging.debug(f"Token à décoder: {token}")

        decoded = jwt.decode(token, secret_key, algorithms=['HS256'])
        return decoded
    except jwt.ExpiredSignatureError:
        raise PermissionError("Token expired")
    except jwt.InvalidTokenError:
        raise PermissionError("Invalid token")
    except Exception as e:
        raise PermissionError(f"Token error: {str(e)}")


def save_session(token):
    try:
        with open('session.json', 'w') as f:
            json.dump({'token': token}, f, indent=4)
        print("Token sauvegardé dans la session.")
    except IOError as e:
        print(f"Erreur lors de l'écriture dans le fichier de session : {e}")


def load_session():
    try:
        with open('session.json', 'r') as file:
            data = json.load(file)
            token = data.get('token')
            if isinstance(token, str):
                return token
            else:
                raise ValueError("Token in session.json must be a string")
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        print(f"Erreur de décodage JSON : {e}")
        return None


def stop_session():
    try:
        os.remove('session.json')
    except OSError:
        pass


def create_session(user, delta, secret=SECRET_KEY):
    token = create_token(user, secret)
    save_session(token)


def renew_session(secret=SECRET_KEY):
    """
    Renouvelle le jeton JWT stocké dans 'session.json'.
    """
    # Vous devrez passer l'utilisateur à cette fonction si nécessaire pour recréer le jeton
    user = get_current_user()
    new_token = create_token(user, secret)

    with open('session.json', 'w') as file:
        json.dump({'token': new_token}, file)

    return new_token


def serialize_user(user):
    """Convertit un objet utilisateur en un dictionnaire sérialisable en JSON."""
    if hasattr(user, 'username') and hasattr(user, 'role'):
        return {
            'username': user.username,
            'role': str(user.role),  # Convertir le rôle en chaîne
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'state': str(user.state)  # Convertir l'état en chaîne
        }
    raise ValueError("L'objet utilisateur n'a pas les attributs requis.")


def read_role(secret=SECRET_KEY):
    """
    Lit le rôle de l'utilisateur à partir du token JWT stocké dans 'session.json'.
    Si le jeton est expiré, renouvelle le jeton et retourne le nouveau.
    """
    token = load_session()
    if not token:
        text = "Aucun jeton trouvé dans la session."
        console.print(text, style="bold red")
        return None

    try:
        decoded = decode_token(token, secret)
        role = decoded.get('role')
        if not role:
            text = "Le rôle dans le jeton est None."
            console.print(text, style="bold red")
            return None
        return role
    except PermissionError as e:
        text = f"Erreur de permission : {e}"
        console.print(text, style="bold red")
        new_token = renew_session(secret)
        return new_token


def get_current_user(secret=SECRET_KEY):
    token = load_session()
    if not token:
        text = "Aucun jeton trouvé dans la session."
        console.print(text, style="bold red")
        return None

    try:
        decoded = decode_token(token, secret)
        username = decoded.get('username')
        if not username:
            text = "Le jeton ne contient pas d'identifiant d'utilisateur."
            console.print(text, style="bold red")
            return None

        user = session.query(EpicUser).filter_by(username=username).first()
        if not user:
            text = f"Utilisateur {username} non trouvé dans la base de données."
            console.print(text, style="bold red")
            return None

        return user
    except PermissionError as e:
        text = f"Erreur de permission : {e}"
        console.print(text, style="bold red")
        return None


def force_refresh_token(secret=SECRET_KEY):
    """
    Force le renouvellement du jeton JWT en le recréant avec les mêmes informations utilisateur.
    """
    # Charger le jeton actuel
    token = load_session()
    if not token:
        text = "Aucun jeton trouvé dans la session."
        console.print(text, style="bold red")
        return None

    try:
        # Décoder le jeton pour obtenir les informations utilisateur
        decoded = jwt.decode(token, secret, algorithms=['HS256'])
        username = decoded.get('username')

        if not username:
            text = "Le jeton ne contient pas d'identifiant d'utilisateur."
            console.print(text, style="bold red")
            return None

        # Récupérer l'utilisateur à partir de la base de données
        user = session.query(EpicUser).filter_by(username=username).first()
        if not user:
            text = f"Utilisateur {username} non trouvé dans la base de données."
            console.print(text, style="bold red")
            return None

        # Créer un nouveau jeton avec les mêmes informations (ou mises à jour)
        new_token = create_token(user, secret)

        # Sauvegarder le nouveau jeton dans 'session.json'
        save_session(new_token)

        return new_token

    except jwt.ExpiredSignatureError:
        text = "Le jeton a expiré. Veuillez vous reconnecter."
        console.print(text, style="bold red")
        return None
    except jwt.InvalidTokenError:
        text = "Jeton invalide."
        console.print(text, style="bold red")
        return None
