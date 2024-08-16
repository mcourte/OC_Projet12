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

    """ connect on db and manage crud operations """

    def __init__(self, database, host, user, password, port=5432) -> None:
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
        try:
            if database_exists(self.url):
                AuthenticationView.display_database_connection(database)
            else:
                data_manager = AuthenticationView.prompt_manager()
                AuthenticationView.display_waiting_databasecreation(
                    self.database_creation, data_manager)
        except Exception:
            data_manager = AuthenticationView.prompt_manager()
            AuthenticationView.display_waiting_databasecreation(
                self.database_creation, data_manager)

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
        self.session.close()
        self.engine.dispose()

    def database_creation(self, username, password):
        create_database(self.url)
        # init database structure
        engine = create_engine(self.url)
        Base.metadata.create_all(engine)
        self.session = scoped_session(sessionmaker(bind=engine))
        self.db_users = EpicUserBase(self.session)
        # add initial data
        self.first_initdb(username, password)
        self.session.remove()

    def check_connection(self, username, password) -> EpicUser:
        user = EpicUser.find_by_username(self.session, username)
        if user:
            print(f"User found: {username}")  # Ajoutez ce genre de messages
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
        Check the username is in database employee
        Args:
            username (str): the username
        Returns:
            Employee: an instance of Employee
        """
        return EpicUser.find_by_username(self.session, username)


class EpicDatabaseWithData(EpicDatabase):

    def first_initdb(self, username, password):
        super().first_initdb(username, password)
        self.create_a_test_database()

    def add_some_contracts(self):
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
        # create a special contract on client0
        customer = Customer.find_by_name(self.session, 'YukaCli')
        new_contract = Contract(
            description="contrat1",
            customer_id=customer.customer_id,
            total_amount=3000,
            state='S'
        )
        self.session.add(new_contract)
        self.session.commit()

    def add_some_clients(self):
        self.db_users.add_user('Magali', 'Courté', 'Commercial', 'password')
        self.db_users.add_user('Pauline', 'Bellec', 'Commercial', 'password')
        commercial_one = EpicUser.find_by_username(self.session, 'mcourte')
        commercial_two = EpicUser.find_by_username(self.session, 'pbellec')
        company_names = ['La Cordée',
                         'Hello Work',
                         'Groupe Legendre']
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
        self.db_users.add_user('Julie', 'Benzonni', 'Gestion', 'password')
        self.db_users.add_user('Aurélien', 'LeFeuvre', 'Gestion', 'password')
        self.db_users.add_user('Maël', 'Thomas', 'Support', 'password')
        support_one = EpicUser.find_by_username(self.session, 'mthomas')
        contracts = Contract.getall(self.session)
        locations = [
            'France',
            'Allemagne',
            'Chine',
            'angleterre',
            'Russie']
        for contract in contracts:
            nb_of_events = randint(1, 10)
            for i in range(nb_of_events):
                title = f'Ev. n°{i}'
                description = f'Un énènement pour notre client {contract.customer}'
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
        # create a specifique event on Legendre Contrat
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
        self.add_some_clients()
        self.add_some_contracts()
        self.add_some_events()
