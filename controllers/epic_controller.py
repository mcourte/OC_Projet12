import jwt
import json
import os
import sys
from controllers.config import Config, Environ
from controllers.database_controller import EpicDatabase
from terminal.terminal_user import EpicTerminalUser
from controllers.session import load_session, stop_session, create_session, save_session
from controllers.session import create_token
from controllers.decorator import is_authenticated
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)
from views.authentication_view import AuthenticationView


class EpicBase:
    """
    Classe principale pour gérer l'application CRM EPIC EVENTS.
    Elle initialise l'environnement, la base de données, et gère la session utilisateur.
    """
    def __init__(self) -> None:
        """
        Initialise la classe EpicBase en chargeant l'environnement,
        en créant la base de données et en vérifiant la session actuelle.
        """
        print("Initialisation de EpicBase...")
        self.env = Environ()
        db_config = self.get_config()
        self.epic = EpicDatabase(**db_config)

        self.current_user = None
        self.epic.users = EpicTerminalUser(self.epic, self.epic.session)

    def get_config(self):
        """
        Récupère la configuration de la base de données à partir de l'environnement.

        Retourne :
        ----------
        dict : Un dictionnaire contenant les paramètres de connexion à la base de données.
        """
        config = Config()
        return {
            'database': config.database,
            'host': config.host,
            'user': config.user,
            'password': config.password,
            'port': config.port
        }

    def login(self, **kwargs) -> bool:
        """
        Gère le processus de connexion de l'utilisateur.

        Paramètres :
        ------------
        **kwargs : dict
            Paramètres optionnels pour la connexion.

        Retourne :
        ----------
        bool : True si la connexion est réussie, sinon False.
        """
        try:
            stop_session()

            username, password = AuthenticationView.prompt_login(**kwargs)
            user_data = self.epic.check_connection(username, password)

            if user_data and hasattr(user_data, 'username') and hasattr(user_data, 'role'):
                self.current_user = user_data

                token = create_token(user_data, self.env.SECRET_KEY)
                create_session(user_data, token)

                print("Connexion réussie")
                return True
            else:
                print("Échec de la connexion")
                return False
        except Exception as e:
            print(f"Erreur lors du processus de connexion : {e}")
            return False

    @is_authenticated
    def check_logout(self) -> bool:
        """
        Arrête la session actuelle et déconnecte l'utilisateur.

        Retourne :
        ----------
        bool : True si la déconnexion est réussie.
        """
        stop_session()
        print("Déconnecté")
        return True

    def load_session():
        """
        Charge le jeton JWT depuis 'session.json'.
        """
        try:
            with open('session.json', 'r') as file:
                data = json.load(file)
                token = data.get('token')

                if isinstance(token, str):
                    return token
                else:
                    raise ValueError("Token in session.json must be a string")
        except FileNotFoundError:
            print("Le fichier de session est introuvable.")
            return None
        except json.JSONDecodeError as e:
            print(f"Erreur de décodage JSON : {e}")
            return None

    def check_session(self):
        """
        Vérifie la session en cours.
        """
        token = load_session()
        if token:
            try:
                # Décoder le jeton JWT
                decoded_token = jwt.decode(token, self.env.SECRET_KEY, algorithms=['HS256'])
                username = decoded_token.get('username')
                if username:
                    user = self.epic.check_user(username)
                    if user:
                        self.user = user
                        return user
            except jwt.ExpiredSignatureError:
                print("Le jeton a expiré.")
                self.refresh_session()
            except jwt.InvalidTokenError:
                print("Jeton invalide.")
        return None

    def refresh_session(self):
        """
        Rafraîchit la session en créant un nouveau jeton et en le stockant.

        Si aucun utilisateur n'est connecté, une erreur est affichée.
        """
        if self.user:
            new_token = create_token(self.user)  # Passez l'objet utilisateur complet
            save_session(new_token)
        else:
            print("Aucun utilisateur connecté pour rafraîchir la session.")

    @classmethod
    def initbase(cls):
        """
        Initialise la base de données et crée un fichier de configuration.

        Demande à l'utilisateur de saisir les informations nécessaires pour la configuration,
        puis crée la base de données et la configure.
        """
        stop_session()
        values = AuthenticationView.prompt_baseinit()  # Suppose (database, username, password, port)
        Config().create_config(*values)  # Appelle create_config avec les arguments appropriés
        db = Config()  # Charge la configuration
        EpicDatabase(database=db.database, host=db.host, user=db.user, password=db.password, port=db.port)
        AuthenticationView.display_database_connection(values[0])

    def authenticate_user(self, username, password):
        # Logique pour authentifier un utilisateur et définir self.user
        user = self.db_users.get_user(username)
        if user and user.check_password(password):
            self.user = user
            return True
        return False
