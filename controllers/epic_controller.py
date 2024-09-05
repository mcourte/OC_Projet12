# Import généraux
import jwt
import os
import sys

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

# Import des Views
from views.authentication_view import AuthenticationView
from views.console_view import console

# Import des Controllers
from controllers.config import Config, Environ
from controllers.database_controller import EpicDatabase
from controllers.session import load_session, clear_session, create_session, save_session, get_current_user
from controllers.session import create_token

# Import des Terminaux
from terminal.terminal_user import EpicTerminalUser, EpicUser


class EpicBase:
    """
    Classe principale pour gérer l'application CRM EPIC EVENTS.

    Cette classe initialise l'environnement, la base de données, et gère la session utilisateur.
    Elle fournit également des méthodes pour la connexion, la vérification et le rafraîchissement de la session utilisateur.
    """

    def __init__(self) -> None:
        """
        Initialise une instance de EpicBase.

        Configure l'environnement, la base de données, et la session utilisateur.
        Affiche les informations de débogage sur l'utilisateur actuel.
        """
        text = "Initialisation de EpicBase..."
        console.print(text, style="bold green")
        self.env = Environ()
        db_config = self.get_config()
        self.epic = EpicDatabase(**db_config)
        self.session = self.epic.session

        self.current_user = None
        self.epic.users = EpicTerminalUser(self.epic, self.epic.session, self.current_user)

        # Obtenez et affichez l'utilisateur actuel pour débogage
        self.current_user = get_current_user()
        if self.current_user:
            text = f"Utilisateur actuel dans EpicBase : {self.current_user}"
            console.print(text, style="green")

        self.epic.users = EpicTerminalUser(self.epic, self.session, self.current_user)

        self.check_session()

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

        Cette méthode demande les informations d'identification de l'utilisateur,
        vérifie leur validité, crée un jeton de session, et initialise la session de l'utilisateur.

        Paramètres :
        ------------
        **kwargs : dict
            Paramètres optionnels pour la connexion.

        Retourne :
        ----------
        bool : True si la connexion est réussie, sinon False.
        """
        try:
            clear_session()

            username, password = AuthenticationView.prompt_login(**kwargs)
            user_data = self.epic.check_connection(username, password)

            if user_data and hasattr(user_data, 'to_dict'):
                self.current_user = user_data

                # Convertir l'utilisateur en dictionnaire
                user_dict = user_data.to_dict()

                token = create_token(user_dict, self.env.SECRET_KEY)
                create_session(user_dict, token)

                text = "Connexion réussie"
                console.print(text, style="bold blue")
                return True
            else:
                text = "Échec de la connexion"
                console.print(text, style="bold blue")
                return False
        except Exception as e:
            text = f"Erreur lors du processus de connexion : {e}"
            console.print(text, style="bold red")
            return False

    def check_session(self):
        """
        Vérifie la session en cours.

        Cette méthode décode le jeton JWT pour valider la session en cours,
        et authentifie l'utilisateur si le jeton est valide. Affiche des messages
        d'erreur si le jeton est invalide ou expiré.

        Retourne :
        ----------
        EpicUser : L'utilisateur actuellement authentifié, ou None si la session est invalide.
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
                        # Authentifier de nouveau l'utilisateur pour assurer qu'il est toujours valide
                        if self.authenticate_user(self.epic.session, username, user.password):
                            self.current_user = self.user
                            return user
                        else:
                            text = "Erreur : Utilisateur non authentifié."
                            console.print(text, style="bold red")
                else:
                    text = "Le jeton ne contient pas de nom d'utilisateur valide."
                    console.print(text, style="bold red")
            except jwt.ExpiredSignatureError:
                text = "Le jeton a expiré."
                console.print(text, style="bold red")
                self.refresh_session()
            except jwt.InvalidTokenError:
                text = "Jeton invalide."
                console.print(text, style="bold red")
        return None

    def refresh_session(self):
        """
        Rafraîchit la session en créant un nouveau jeton et en le stockant.

        Cette méthode crée un nouveau jeton pour l'utilisateur actuel, si un utilisateur est connecté.
        Affiche un message d'erreur si aucun utilisateur n'est connecté.
        """
        if self.current_user:
            new_token = create_token(self.current_user)
            save_session(new_token)
        else:
            text = "Aucun utilisateur connecté pour rafraîchir la session."
            console.print(text, style="bold red")

    def authenticate_user(self, session, username, password):
        """
        Authentifie un utilisateur en vérifiant son nom d'utilisateur et son mot de passe.

        Cette méthode recherche l'utilisateur dans la base de données et vérifie
        son mot de passe. Si l'utilisateur est trouvé et authentifié, il est défini
        comme l'utilisateur actuel.

        Paramètres :
        ------------
        session : SQLAlchemy Session
            La session de base de données pour exécuter la requête.
        username : str
            Le nom d'utilisateur de l'utilisateur à authentifier.
        password : str
            Le mot de passe de l'utilisateur à authentifier.

        Retourne :
        ----------
        bool : True si l'utilisateur est authentifié avec succès, sinon False.
        """
        user = session.query(EpicUser).filter_by(username=username).first()
        if user and user.check_password(password):
            self.user = user
            self.current_user = user  # Assurez-vous de définir current_user ici
            return True
        return False
