import jwt
from views.authentication_view import AuthenticationView
from .config import Config, Environ, create_config
from .database_controller import EpicDatabase
from .session import load_session, stop_session, create_session, save_session
from .decorator import is_authenticated
from utils.jwt_utils import create_token, decode_token


class EpicBase:

    def __init__(self) -> None:
        # load .env file
        self.env = Environ()

        # create database
        db_config = self.get_config()
        self.epic = EpicDatabase(**db_config)

        # lit la session courante
        self.user = self.check_session()

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
        """
        Stop the current session
        Returns:
            bool: always return True
        """
        stop_session()
        print("déconnecté")
        return True

    def login(self, **kwargs) -> bool:
        """Stop session and create a new one after prompt login

        Returns:
            bool: True if login is ok
        """
        stop_session()

        username = kwargs.get('username')
        password = kwargs.get('password')

        # Créez un jeton et affichez-le pour le débogage
        token = create_token({'username': username})
        print(f"Token créé: {token}")

        # Décodez le jeton et affichez les données décodées
        decoded_data = decode_token(token)
        print(f"Data décodée: {decoded_data}")

        # Vérifiez la connexion de l'utilisateur
        e = self.epic.check_connection(username, password)
        if e:
            create_session(e, self.env.TOKEN_DELTA, self.env.SECRET_KEY)
            return True
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
                        return e
            except jwt.ExpiredSignatureError:
                print("Le jeton a expiré.")
                # Gérer le cas de jeton expiré, par exemple en redirigeant vers la page de connexion
                return None
            except jwt.InvalidTokenError:
                print("Jeton invalide.")
                # Gérer le cas de jeton invalide
                return None
        return None

    def refresh_session(self):
        if self.user:
            # Créez un nouveau jeton pour l'utilisateur
            new_token = create_token({'username': self.user.username})
            # Stockez le nouveau jeton
            save_session(new_token)

    @classmethod
    def initbase(cls):
        stop_session()
        values = AuthenticationView.prompt_baseinit()

        file = create_config(*values)
        db = Config(file)
        EpicDatabase(**db.db_config)
        AuthenticationView.display_database_connection(values[0])
