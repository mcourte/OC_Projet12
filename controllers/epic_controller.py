import jwt
from views.authentication_view import AuthenticationView
from .config import Config, Environ, create_config
from .database_controller import EpicDatabase
from .session import load_session, stop_session, create_session
from .decorator import is_authenticated


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
        """ stop session and create a new one after prompt login

        Returns:
            bool: True if login is ok
        """
        stop_session()
        username, password = AuthenticationView.prompt_login(**kwargs)
        e = self.epic.check_connection(username, password)
        if e:
            create_session(e, self.env.TOKEN_DELTA, self.env.SECRET_KEY)
            return True
        else:
            return False

    def check_session(self):
        token = load_session()
        if token:
            user_info = jwt.decode(
                            token, self.env.SECRET_KEY, algorithms=['HS256'])
            print("User info from token:", user_info)  # For debugging
            username = user_info.get('username')  # Use .get() to avoid KeyError
            if username:
                e = self.epic.check_user(username)
                if e:
                    return e

    def refresh_session(self):
        create_session(self.user, self.env.TOKEN_DELTA, self.env.SECRET_KEY)

    @classmethod
    def initbase(cls):
        stop_session()
        values = AuthenticationView.prompt_baseinit()

        file = create_config(*values)
        db = Config(file)
        EpicDatabase(**db.db_config)
        AuthenticationView.display_database_connection(values[0])
