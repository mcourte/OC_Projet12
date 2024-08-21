import jwt
from views.authentication_view import AuthenticationView
from .config import Config, Environ, create_config
from .database_controller import EpicDatabase
from .session import load_session, stop_session, create_session, save_session, create_token, decode_token
from .decorator import is_authenticated


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
        # Charger le fichier .env
        self.env = Environ()

        # Créer la base de données
        db_config = self.get_config()
        self.epic = EpicDatabase(**db_config)

        # Charger la session actuelle
        self.user = None
        self.check_session()

    def __str__(self) -> str:
        return "CRM EPIC EVENTS"

    def get_config(self):
        """
        Récupère la configuration de la base de données à partir de l'environnement.

        Retourne :
        ----------
        dict : Un dictionnaire contenant les paramètres de connexion à la base de données.
        """
        db_url = self.env.DEFAULT_DATABASE
        if db_url.startswith("postgresql"):
            from sqlalchemy.engine.url import make_url
            url = make_url(db_url)
            return {
                'host': url.host,
                'user': url.username,
                'password': url.password,
                'database': url.database,
                'port': url.port
            }
        else:
            config = Config(db_url)
            return config.db_config

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
        stop_session()

        # Obtenez les identifiants depuis l'interface utilisateur
        username, password = AuthenticationView.prompt_login(**kwargs)

        # Vérifiez la connexion
        user_data = self.epic.check_connection(username, password)

        if user_data:
            # Vérifie que `user_data` est un objet avec les attributs requis
            if hasattr(user_data, 'username') and hasattr(user_data, 'role'):
                username = user_data.username
                role = user_data.role

                # Créez le jeton en utilisant les données extraites
                token = create_token(user_data, self.env.SECRET_KEY)
                print(f"Token créé: {token}")

                decoded_data = decode_token(token)
                print(f"Data décodée: {decoded_data}")

                create_session(user_data, self.env.TOKEN_DELTA, self.env.SECRET_KEY)
                self.user = user_data  # Assurez-vous que `self.user` est également un objet approprié
                return True
            else:
                print("L'objet user_data ne contient pas les attributs requis.")
                return False
        else:
            print("Échec de la connexion")
            return False

    def check_session(self):
        """
        Vérifie la session en cours en décodant le jeton stocké.

        Retourne :
        ----------
        EpicUser : L'utilisateur actuel si la session est valide, sinon None.
        """
        token = load_session()
        if token:
            try:
                user_info = jwt.decode(token, self.env.SECRET_KEY, algorithms=['HS256'])
                username = user_info.get('username')
                if username:
                    e = self.epic.check_user(username)
                    if e:
                        self.user = e
                        return e
            except jwt.ExpiredSignatureError:
                print("Le jeton a expiré.")
                # Rafraîchissez la session
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
        values = AuthenticationView.prompt_baseinit()
        file = create_config(*values)
        db = Config(file)
        EpicDatabase(**db.db_config)
        AuthenticationView.display_database_connection(values[0])
