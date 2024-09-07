import pytest
from models.entities import Customer, EpicUser
from terminal.terminal_customer import EpicTerminalCustomer
from views.customer_view import CustomerView
from views.user_view import UserView
from controllers.epic_controller import EpicDatabase
from controllers.session import create_engine, sessionmaker
from datetime import datetime


@pytest.fixture(scope='module')
def test_session():
    db = EpicDatabase(database='app_db', host='localhost', user='mcourte', password='your_password')
    engine = create_engine(db.get_engine_url())
    Session = sessionmaker(bind=engine)
    session = Session()

    # Supprimer les utilisateurs spécifiques s'ils existent
    usernames_to_delete = ['jdoe', 'cdoe', 'jbeam', 'nuser', 'dlefranc', 'alagadec', 'ccelton', 'abeccera']
    for username in usernames_to_delete:
        user_to_delete = session.query(EpicUser).filter_by(username=username).first()
        if user_to_delete:
            session.delete(user_to_delete)
            session.commit()

    # Supprimer les clients spécifiques s'ils existent
    customers_to_delete = ['100', '150', '281', '312', '350']
    for customer_id in customers_to_delete:
        customer_to_delete = session.query(Customer).filter_by(customer_id=customer_id).first()
        if customer_to_delete:
            session.delete(customer_to_delete)
            session.commit()

    yield session
    session.close()


@pytest.fixture
def epic_database():
    db = EpicDatabase(database='app_db', host='localhost', user='mcourte', password='your_password')
    yield db


@pytest.fixture
def current_user(test_session):
    return test_session.query(EpicUser).filter_by(username="mcourte").first()


@pytest.fixture
def setup_customer_terminal(epic_database, test_session, current_user):
    return EpicTerminalCustomer(epic_database, test_session, current_user)


def test_list_of_customers(setup_customer_terminal, test_session, mocker):
    try:
        # Création de clients dans la base de données
        customer1 = test_session.query(Customer).filter_by(customer_id=100).first()
        if not customer1:
            customer1 = Customer(customer_id=100, first_name="John", last_name="Doe",
                                 email="jd@gmail.com", phone="000000000000", company_name="Legendre",
                                 creation_time=datetime.now(), update_time=datetime.now())
            test_session.add(customer1)

        customer2 = test_session.query(Customer).filter_by(customer_id=150).first()
        if not customer2:
            customer2 = Customer(customer_id=150, first_name="Jane", last_name="Smith",
                                 email="js@gmail.com", phone="000000000000", company_name="Cordee",
                                 creation_time=datetime.now(), update_time=datetime.now())
            test_session.add(customer2)

        test_session.commit()

        # Mock pour l'affichage des clients
        mocker.patch.object(CustomerView, 'display_list_customers', return_value=None)

        # Appel de la méthode à tester
        setup_customer_terminal.list_of_customers(test_session)

        # Vérification que les clients sont listés
        customers = test_session.query(Customer).all()
        assert len(customers) == 2
    except Exception as e:
        test_session.rollback()
        raise e


def test_update_customer_commercial(setup_customer_terminal, test_session, mocker):
    try:
        # Création d'un client sans commercial et d'un commercial
        customer = Customer(customer_id=281, first_name="John", last_name="Doe", email='blalba@gmail.com', phone="000000000",
                            company_name="Test", commercial_id=None, creation_time=datetime.now(), update_time=datetime.now())
        commercial = EpicUser(
            role='COM',
            first_name='Damien',
            last_name='Lefranc',
            username='dlefranc',
            password='securepassword',
            email='dlefranc@epic.com',
            state='A'
        )
        test_session.add_all([customer, commercial])
        test_session.commit()

        # Mock des sélections de client et de commercial
        mocker.patch.object(CustomerView, 'prompt_client', return_value=customer.customer_id)
        mocker.patch.object(UserView, 'prompt_commercial', return_value=commercial.username)

        # Appel de la méthode à tester
        setup_customer_terminal.update_customer_commercial(test_session)

        # Vérification que le commercial a bien été attribué au client
        updated_customer = test_session.query(Customer).filter_by(customer_id=281).first()
        assert updated_customer.commercial_id == commercial.epicuser_id
    except Exception as e:
        test_session.rollback()
        raise e


def test_create_customer_as_commercial(setup_customer_terminal, test_session, mocker):
    try:
        # Simulation d'un utilisateur Commercial
        current_user = EpicUser(
            role='COM',
            first_name='Aurélie',
            last_name='Beccera',
            username='abeccera',
            password='securepassword',
            email='abeccera@epic.com',
            state='A'
        )
        setup_customer_terminal.current_user = current_user

        # Mock pour la saisie des données du client
        customer_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "0000000000",
            "company_name": "Cordée",
            "creation_time": datetime.now()
        }
        mocker.patch.object(CustomerView, 'prompt_data_customer', return_value=customer_data)

        # Appel de la méthode à tester
        setup_customer_terminal.create_customer(test_session)

        # Vérification que le client a été créé
        created_customer = test_session.query(Customer).filter_by(first_name="John", last_name="Doe").first()
        assert created_customer is not None
        assert created_customer.commercial_id == current_user.epicuser_id
    except Exception as e:
        test_session.rollback()
        raise e


def test_update_customer(setup_customer_terminal, test_session, mocker):
    try:
        # Création d'un client associé à un commercial
        commercial = EpicUser(
            role='COM',
            first_name='Catherine',
            last_name='Celton',
            username='ccelton',
            password='securepassword',
            email='ccelton@epic.com',
            state='A'
        )
        customer = Customer(customer_id=312, first_name="John", last_name="Doe", phone="0000000000", company_name="Test",
                            email="test@gmail.com", commercial_id=commercial.epicuser_id, creation_time=datetime.now(),
                            update_time=datetime.now())
        test_session.add_all([commercial, customer])
        test_session.commit()

        # Mock pour sélectionner le client et saisir de nouvelles données
        mocker.patch.object(CustomerView, 'prompt_client', return_value=customer.customer_id)
        mocker.patch.object(CustomerView, 'prompt_data_customer', return_value={"first_name": "Jane", "last_name": "Doe"})

        # Appel de la méthode à tester
        setup_customer_terminal.update_customer(test_session)

        # Vérification que les informations du client ont été mises à jour
        updated_customer = test_session.query(Customer).filter_by(customer_id=1).first()
        assert updated_customer.first_name == "Jane"
        assert updated_customer.last_name == "Doe"
    except Exception as e:
        test_session.rollback()
        raise e


def test_add_customer_commercial(setup_customer_terminal, test_session, mocker):
    try:
        # Vérifier si un client avec cet email existe déjà
        existing_customer = test_session.query(Customer).filter_by(email="cacacaca@gmail.com").first()
        if not existing_customer:
            customer = Customer(
                customer_id=350,
                first_name="John",
                last_name="Doe",
                commercial_id=None,
                phone="0000000000",
                company_name="Test",
                email="cacacaca@gmail.com",
                creation_time=datetime.now(),
                update_time=datetime.now()
            )
            test_session.add(customer)

        commercial = EpicUser(
            role='COM',
            first_name='Anne-Marie',
            last_name='Lagadec',
            username='alagadec',
            password='securepassword',
            email='alagadec@epic.com',
            state='A'
        )
        test_session.add(commercial)
        test_session.commit()

        # Mock pour sélectionner le commercial
        mocker.patch.object(UserView, 'prompt_commercial', return_value="alagadec")

        # Appel de la méthode à tester
        setup_customer_terminal.add_customer_commercial(test_session, existing_customer)

        # Vérification que le commercial a bien été attribué au client
        updated_customer = test_session.query(Customer).filter_by(customer_id=350).first()
        assert updated_customer.commercial_id == commercial.epicuser_id
    except Exception as e:
        test_session.rollback()
        raise e
