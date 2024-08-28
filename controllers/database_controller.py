import os
import sys
from argon2.exceptions import VerifyMismatchError
from sqlalchemy import create_engine
from sqlalchemy_utils.functions import (
    database_exists,
    create_database
)
from sqlalchemy.orm import (
    sessionmaker,
    scoped_session)

from controllers.user_controller import EpicUserBase


# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)
from models.entities import (
    Base, EpicUser)
from views.authentication_view import AuthenticationView
from views.console_view import console
from terminal.terminal_contract import EpicTerminalContract
from terminal.terminal_customer import EpicTerminalCustomer
from terminal.terminal_user import EpicTerminalUser
from terminal.terminal_event import EpicTerminalEvent


class EpicDatabase:
    def __init__(self, database, host, user, password, port=5432) -> None:
        self.url = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'
        self.engine = create_engine(self.url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.name = database
        self.session = scoped_session(sessionmaker(bind=self.engine))

        if database_exists(self.url):
            text = f"Connexion à la base de données {database} réussie."
            console.print(text, style="green")
        else:
            text = 'Erreur de connexion à la base de données'
            console.print(text, style="bold red")

        # Vous devez maintenant passer un utilisateur valide lors de l'instanciation
        self.current_user = None
        # Passer self.engine et self.session correctement
        self.users = EpicTerminalUser(self.engine, self.session)
        self.customers = EpicTerminalCustomer(self.engine, self.session, self.current_user)
        self.contracts = EpicTerminalContract(self.engine, self.session)
        self.events = EpicTerminalEvent(self.engine, self.session)

    def __str__(self) -> str:
        return f'{self.name} database'

    def database_disconnect(self):
        """
        Déconnecte la session de la base de données et ferme le moteur.
        """
        self.session.close()
        self.engine.dispose()

    def database_creation(self, username, password):
        """
        Crée la base de données et initialise sa structure avec les tables nécessaires.

        Paramètres :
        ------------
        username : str
            Le nom d'utilisateur à ajouter dans la base.
        password : str
            Le mot de passe pour l'utilisateur.
        """
        create_database(self.url)
        # Initialisation de la structure de la base de données
        engine = create_engine(self.url)
        Base.metadata.create_all(engine)
        self.session = scoped_session(sessionmaker(bind=engine))
        self.db_users = EpicUserBase(self.session)
        # Ajout des données initiales
        self.first_initdb(username, password)
        self.session.remove()

    def check_connection(self, username, password) -> EpicUser:
        """
        Vérifie la connexion d'un utilisateur avec ses identifiants.

        Paramètres :
        ------------
        username : str
            Le nom d'utilisateur.
        password : str
            Le mot de passe de l'utilisateur.

        Retourne :
        ----------
        EpicUser : L'utilisateur correspondant si la connexion est réussie.
        """
        user = EpicUser.find_by_username(self.session, username)
        if user:
            try:
                if user.check_password(password):
                    AuthenticationView.display_database_connection(self.name)
                    return user
                else:
                    text = "Le mot de passe est incorrect"
                    console.print(text, style="bold red")
                    pass
            except VerifyMismatchError as e:
                print(f"Password verification error: {e}")
        else:
            print(f"No user found with username: {username}")
        return None

    def check_user(self, username) -> EpicUser:
        """
        Vérifie si un nom d'utilisateur est présent dans la base de données des employés.

        Paramètres :
        ------------
        username : str
            Le nom d'utilisateur à vérifier.

        Retourne :
        ----------
        EpicUser : L'utilisateur correspondant, ou None s'il n'existe pas.
        """
        return EpicUser.find_by_username(self.session, username)
