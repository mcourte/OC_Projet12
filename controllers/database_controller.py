# Import généraux
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


# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)
from models.entities import (
    Base, EpicUser)

# Import des Views
from views.authentication_view import AuthenticationView
from views.console_view import console

# Import Terminaux
from terminal.terminal_contract import EpicTerminalContract
from terminal.terminal_customer import EpicTerminalCustomer
from terminal.terminal_user import EpicTerminalUser
from terminal.terminal_event import EpicTerminalEvent

# Import Controllers
from controllers.user_controller import EpicUserBase


class EpicDatabase:
    def __init__(self, database, host, user, password, port=5432) -> None:
        """
        Initialise une connexion à une base de données PostgreSQL.

        Paramètres :
        ------------
        database : str
            Le nom de la base de données à utiliser.
        host : str
            L'hôte du serveur de base de données.
        user : str
            Le nom d'utilisateur pour se connecter à la base de données.
        password : str
            Le mot de passe pour l'utilisateur.
        port : int, optionnel
            Le port du serveur de base de données (par défaut : 5432).
        """
        self.url = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'
        self.engine = create_engine(self.url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session = scoped_session(self.SessionLocal)  # Utilise scoped_session ici

        if database_exists(self.url):
            text = f"Connexion à la base de données {database} réussie."
            console.print(text, style="green")
        else:
            text = 'Erreur de connexion à la base de données'
            console.print(text, style="bold red")
        self.name = database
        self.current_user = None
        self.users = EpicTerminalUser(self.engine, self.session)
        self.customers = EpicTerminalCustomer(self.engine, self.session, self.current_user)
        self.contracts = EpicTerminalContract(self.engine, self.session)
        self.events = EpicTerminalEvent(self.engine, self.session)

    def __str__(self) -> str:
        """
        Retourne une représentation en chaîne de caractères de l'objet EpicDatabase.

        Retourne :
        ----------
        str
            Une chaîne de caractères décrivant le nom de la base de données.
        """
        return f'{self.name} database'

    def database_disconnect(self):
        """
        Déconnecte la session de la base de données et ferme le moteur.

        Cette méthode est utilisée pour libérer les ressources liées à la connexion
        à la base de données lorsque l'application n'en a plus besoin.
        """
        self.session.close()
        self.engine.dispose()

    def database_creation(self, username, password):
        """
        Crée la base de données et initialise sa structure avec les tables nécessaires.

        Paramètres :
        ------------
        username : str
            Le nom d'utilisateur à ajouter dans la base de données.
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
        EpicUser
            L'utilisateur correspondant si la connexion est réussie, sinon None.
        """
        user = self.session.query(EpicUser).filter_by(username=username).first()
        if user:
            try:
                if user.check_password(password):
                    AuthenticationView.display_database_connection(self.name)
                    return user
                else:
                    text = "Le mot de passe est incorrect"
                    console.print(text, style="bold red")
            except VerifyMismatchError as e:
                text = f"Erreur de vérification du mot de passe : {e}"
                console.print(text, style="bold red")
        else:
            text = f"Aucun utilisateur trouvé avec le nom d'utilisateur : {username}"
            console.print(text, style="bold red")
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
        EpicUser
            L'utilisateur correspondant si trouvé, sinon None.
        """
        return EpicUser.find_by_username(self.session, username)
