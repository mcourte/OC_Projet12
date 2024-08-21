from argon2.exceptions import VerifyMismatchError
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy_utils.functions import (
    database_exists,
    create_database
)
from sqlalchemy.orm import (
    sessionmaker,
    scoped_session
    )
from models.entities import (
    Base, EpicUser, Support, Customer, Contract, Event)
from views.authentication_view import AuthenticationView

import random
from datetime import datetime, timedelta, timezone
from random import randint
from psycopg2.errors import UniqueViolation
from controllers.contract_controller import ContractBase
from controllers.user_controller import EpicUserBase
from controllers.event_controller import EventBase
from controllers.customer_controller import CustomerBase


class EpicDatabase:
    """ Connexion à la base de données et gestion des opérations CRUD """

    def __init__(self, database, host, user, password, port=5432) -> None:
        """
        Initialise la classe EpicDatabase avec les paramètres de connexion.

        Paramètres :
        ------------
        database : str
            Le nom de la base de données.
        host : str
            L'hôte de la base de données.
        user : str
            Le nom d'utilisateur pour la connexion.
        password : str
            Le mot de passe pour la connexion.
        port : int, optionnel
            Le port de connexion à la base de données (par défaut 5432).
        """
        # Si le port est None, attribuer une valeur par défaut
        if port is None:
            port = 5432

        self.url = URL.create(
            drivername="postgresql",
            database=database,
            host=host,
            username=user,
            password=password,
            port=int(port)
        )

        print(f'checking {self.url} ...')
        if database_exists(self.url):
            AuthenticationView.display_database_connection(database)
        else:
            print('erreur')

        self.name = database
        self.engine = create_engine(self.url)

        self.session = scoped_session(sessionmaker(bind=self.engine))
        self.db_users = EpicUserBase(self.session)
        self.db_customers = CustomerBase(self.session)
        self.db_contracts = ContractBase(self.session)
        self.db_events = EventBase(self.session)

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
            print(f"User found: {username}")
            try:
                if user.check_password(password):
                    AuthenticationView.display_database_connection(self.name)
                    return user
                else:
                    print("Password does not match")
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


class EpicDatabaseWithData(EpicDatabase):
    """
    Classe dérivée de EpicDatabase qui ajoute des méthodes pour initialiser
    la base de données avec des données de test.
    """

    def first_initdb(self, username, password):
        """
        Initialise la base de données en ajoutant des données de test après la création initiale.

        Paramètres :
        ------------
        username : str
            Le nom d'utilisateur à ajouter dans la base.
        password : str
            Le mot de passe pour l'utilisateur.
        """
        super().first_initdb(username, password)
        self.create_a_test_database()

    def add_some_contracts(self):
        """
        Ajoute des contrats aléatoires à la base de données pour les clients existants.
        """
        customers = Customer.getall(self.session)
        for customer in customers:
            nb_of_contracts = randint(0, 10)
            for i in range(nb_of_contracts):
                contract_description = f"Contract {i} for {customer.last_name}"
                state = random.choice(Contract.CONTRACT_STATES)[0]
                new_contract = Contract(
                    description=contract_description,
                    customer_id=customer.customer_id,
                    total_amount=randint(500, 30000),
                    state=state
                )
                self.session.add(new_contract)
                try:
                    self.session.commit()
                except UniqueViolation:
                    pass
        # Crée un contrat spécial pour le client "Blattner"
        customer = Customer.find_by_name(self.session, 'Blattner')
        new_contract = Contract(
            description="contrat1",
            customer_id=customer.customer_id,
            total_amount=3000,
            state='S'
        )
        self.session.add(new_contract)
        self.session.commit()

    def add_some_clients(self):
        """
        Ajoute quelques clients et leurs informations à la base de données.
        """
        self.db_users.add_user('Magali', 'Courté', 'Commercial', 'password')
        self.db_users.add_user('Pauline', 'Bellec', 'Commercial', 'password')
        commercial_one = EpicUser.find_by_username(self.session, 'mcourte')
        commercial_two = EpicUser.find_by_username(self.session, 'pbellec')
        company_names = ['La Cordée', 'Hello Work', 'Groupe Legendre']
        customer_one = Customer(
            first_name='Vincent',
            last_name='Legendre',
            email='courte.magali@gmail.com',
            phone='111-1111-1111',
            company_name='Groupe Legendre',
            commercial_id=commercial_one.epicuser_id)
        self.session.add(customer_one)
        customer_two = Customer(
            first_name='Marion',
            last_name='Blattner',
            email='courte.magali@gmail.com',
            phone='111-1111-1111',
            company_name=random.choice(company_names),
            commercial_id=random.choice([commercial_one.epicuser_id, commercial_two.epicuser_id])
        )
        self.session.add(customer_two)
        self.session.commit()

    def add_some_events(self):
        """
        Ajoute des événements aléatoires à la base de données pour les contrats existants.
        """
        self.db_users.add_user('Julie', 'Benzonni', 'Gestion', 'password')
        self.db_users.add_user('Aurélien', 'LeFeuvre', 'Gestion', 'password')
        self.db_users.add_user('Maël', 'Thomas', 'Support', 'password')
        support_one = EpicUser.find_by_username(self.session, 'mthomas')
        contracts = Contract.getall(self.session)
        locations = [
            'France',
            'Allemagne',
            'Chine',
            'Angleterre',
            'Russie']
        for contract in contracts:
            nb_of_events = randint(1, 10)
            for i in range(nb_of_events):
                title = f'Ev. n°{i}'
                description = f'Un événement pour notre client {contract.customer}'
                nb = randint(10, 200)
                nbj_start = randint(1, 300)
                nbh_end = randint(1, 240)
                date_start = datetime.now(tz=timezone.utc)\
                    + timedelta(days=nbj_start)
                date_end = date_start\
                    + timedelta(hours=nbh_end)
                state = random.choice(Event.EVENT_STATES)
                somewhere = random.choice(locations)
                event_one = Event(
                    title=title, description=description,
                    attendees=nb, location=somewhere,
                    date_started=date_start,
                    date_ended=date_end,
                    state=state,
                    contract_id=contract.contract_id,
                )
                is_support = randint(0, 3)
                if is_support:
                    users = Support.getall(self.session)
                    support = random.choice(users)
                    support_one.support_id = support.id
                self.session.add(event_one)
        # Crée un événement spécifique pour le contrat "Legendre"
        contracts = Contract.getall(self.session)
        for contract in contracts:
            last_name = contract.last_name
            if last_name == 'Legendre':
                contract_choosen = contract
        nbj_start = randint(1, 300)
        nbh_end = randint(1, 240)
        mthomas = Support.find_by_username(self.session, 'mthomas')
        event = Event(
            title='Mael event', description='Mael event',
            attendees=10, location='Rennes',
            date_started="2023-10-07 15:00:00.000000",
            date_ended="2023-10-07 17:00:00.000000",
            contract_id=contract_choosen.contract_id,
            support_id=mthomas.epicuser_id
        )
        self.session.add(event)
        self.session.commit()

    def create_a_test_database(self):
        """
        Crée une base de données de test en ajoutant des clients, des contrats et des événements.
        """
        self.add_some_clients()
        self.add_some_contracts()
        self.add_some_events()
