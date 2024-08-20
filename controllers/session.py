import os
import sys
import json
import jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from models.entities import EpicUser

# Configuration de la session SQLAlchemy
engine = create_engine('postgresql://postgres:password@localhost:5432/app_db')
Session = sessionmaker(bind=engine)
session = Session()

SECRET_KEY = 'openclassroom_projet12'
ALGORITHM = 'HS256'


def create_token(user, secret=SECRET_KEY):
    """
    Crée un jeton JWT pour un utilisateur avec son rôle.
    """
    # Vérifiez si le rôle de l'utilisateur est défini et non nul
    if not hasattr(user, 'role') or not user.role:
        raise ValueError("Le rôle de l'utilisateur ne peut pas être None")

    # Récupérer le code ou la valeur du rôle
    role_value = user.role.code if hasattr(user.role, 'code') else str(user.role)

    # Utilisation de timezone.utc pour avoir une datetime aware
    payload = {
        'username': user.username,
        'role': role_value,  # Utiliser le code ou la valeur du rôle ici
        'exp': datetime.now(timezone.utc) + timedelta(hours=4)  # Jeton valide pour 4 heures
    }
    print(f"Payload pour le jeton: {payload}")  # Ligne de débogage pour vérifier le payload
    token = jwt.encode(payload, secret, algorithm='HS256')
    return token


def decode_token(token):
    """ Décode un jeton et renvoie les données """
    print(f"Token before decode: {token}")
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    print(f"Decoded token: {decoded_token}")

    return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])


def create_session(user, delta, secret=SECRET_KEY):
    """
    Crée une session pour un utilisateur avec un jeton JWT.
    """
    # Vérification du type et de la valeur de `user.role`
    print(f"Type de user.role: {type(user.role)}, Valeur de user.role: {user.role}")

    # Récupération de la valeur du rôle, en le convertissant en chaîne si nécessaire
    role_value = user.role.code if hasattr(user.role, 'code') else str(user.role)

    # Création du token en utilisant la fonction create_token
    token = create_token(user, secret)

    print(f"Creating session with role: {role_value}")

    # Debugging line to check the token content
    decoded = jwt.decode(token, secret, algorithms=['HS256'])
    print(f"Token content: {decoded}")

    save_session(token)


def renew_session(secret=SECRET_KEY):
    """
    Renouvelle le jeton JWT stocké dans 'session.json'.
    """
    # Vous devrez passer l'utilisateur à cette fonction si nécessaire pour recréer le jeton
    user = get_current_user()  # Remplacez ceci par la méthode pour obtenir l'utilisateur courant
    new_token = create_token(user, secret)

    with open('session.json', 'w') as file:
        json.dump({'token': new_token}, file)

    return new_token


def save_session(token):
    """
    Save the JWT token to 'session.json'.
    """
    with open('session.json', 'w') as f:
        json.dump({'token': token}, f, indent=4)


def load_session():
    """
    Charge le jeton JWT depuis 'session.json'.
    """
    try:
        with open('session.json', 'r') as file:
            data = json.load(file)
            return data.get('token')
    except FileNotFoundError:
        return None


def stop_session():
    """
    Delete 'session.json' file to stop the session.
    """
    try:
        os.remove('session.json')
    except OSError:
        pass


def read_role(secret=SECRET_KEY):
    """
    Lit le rôle de l'utilisateur à partir du token JWT stocké dans 'session.json'.
    Si le jeton est expiré, renouvelle le jeton et retourne le nouveau.
    """
    token = load_session()
    if not token:
        print("Aucun jeton trouvé dans la session.")
        return None

    print(f"Jeton chargé : {token}")  # Ligne de débogage

    try:
        decoded = jwt.decode(token, secret, algorithms=['HS256'])
        print(f"Données décodées : {decoded}")  # Ligne de débogage
        role = decoded.get('role')
        if not role:
            print("Le rôle dans le jeton est None.")
            return None
        print(f"Role récupéré du token : {role}")  # Ligne de débogage
        return role
    except jwt.ExpiredSignatureError:
        print("Le jeton a expiré. Veuillez vous reconnecter.")
        new_token = renew_session(secret)
        return new_token
    except jwt.InvalidTokenError:
        print("Token invalide.")
        return None


def get_current_user():
    """
    Récupère l'utilisateur actuel à partir du jeton JWT stocké dans 'session.json'.
    """
    token = load_session()
    if not token:
        print("Aucun jeton trouvé dans la session.")
        return None

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        print(f"Données décodées : {decoded}")  # Impression de débogage
        username = decoded.get('username')
        if not username:
            print("Le jeton ne contient pas d'identifiant d'utilisateur.")
            return None

        user = session.query(EpicUser).filter_by(username=username).first()
        if not user:
            print(f"Utilisateur {username} non trouvé dans la base de données.")
            return None

        return user

    except jwt.ExpiredSignatureError:
        print("Le jeton a expiré. Veuillez vous reconnecter.")
        return None
    except jwt.InvalidTokenError:
        print("Jeton invalide.")
        return None


def force_refresh_token(secret=SECRET_KEY):
    """
    Force le renouvellement du jeton JWT en le recréant avec les mêmes informations utilisateur.
    """
    # Charger le jeton actuel
    token = load_session()
    if not token:
        print("Aucun jeton trouvé dans la session.")
        return None

    try:
        # Décoder le jeton pour obtenir les informations utilisateur
        decoded = jwt.decode(token, secret, algorithms=['HS256'])
        username = decoded.get('username')

        if not username:
            print("Le jeton ne contient pas d'identifiant d'utilisateur.")
            return None

        # Récupérer l'utilisateur à partir de la base de données
        user = session.query(EpicUser).filter_by(username=username).first()
        if not user:
            print(f"Utilisateur {username} non trouvé dans la base de données.")
            return None

        # Créer un nouveau jeton avec les mêmes informations (ou mises à jour)
        new_token = create_token(user, secret)

        # Sauvegarder le nouveau jeton dans 'session.json'
        save_session(new_token)

        print(f"Nouveau jeton généré : {new_token}")
        return new_token

    except jwt.ExpiredSignatureError:
        print("Le jeton a expiré. Veuillez vous reconnecter.")
        return None
    except jwt.InvalidTokenError:
        print("Jeton invalide.")
        return None


if __name__ == '__main__':
    # Suppose que vous avez un utilisateur EpicUser pour lequel vous souhaitez créer un jeton
    user = session.query(EpicUser).filter_by(username="mcourte").first()
    if user:
        new_token = create_token(user)
        save_session(new_token)
        print(f"Jeton enregistré : {new_token}")
    else:
        print("Utilisateur non trouvé.")
