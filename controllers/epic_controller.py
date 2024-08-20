import jwt
from views.authentication_view import AuthenticationView
from .config import Config, Environ, create_config
from .database_controller import EpicDatabase
from .session import load_session, stop_session, create_session, save_session, create_token, decode_token
from .decorator import is_authenticated


class EpicBase:
    def __init__(self) -> None:
        # Load .env file
        self.env = Environ()

        # Create database
        db_config = self.get_config()
        self.epic = EpicDatabase(**db_config)

        # Load current session
        self.user = None
        self.check_session()

    def __str__(self) -> str:
        return "CRM EPIC EVENTS"

    def get_config(self):
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
        """ Stop the current session """
        stop_session()
        print("Déconnecté")
        return True

    def login(self, **kwargs) -> bool:
        stop_session()

        # Obtenez les identifiants depuis l'interface utilisateur
        username, password = AuthenticationView.prompt_login(**kwargs)

        # Vérifiez la connexion
        user_data = self.epic.check_connection(username, password)

        if user_data:
            # Assurez-vous que `user_data` est un objet avec les attributs appropriés
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
        """ Refresh the session and store the new token """
        if self.user:
            new_token = create_token(self.user)  # Pass the complete user object
            save_session(new_token)
        else:
            print("Aucun utilisateur connecté pour rafraîchir la session.")

    @classmethod
    def initbase(cls):
        stop_session()
        values = AuthenticationView.prompt_baseinit()
        file = create_config(*values)
        db = Config(file)
        EpicDatabase(**db.db_config)
        AuthenticationView.display_database_connection(values[0])
