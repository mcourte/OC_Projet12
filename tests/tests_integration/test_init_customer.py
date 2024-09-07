import pytest
from models.entities import Customer, EpicUser, Commercial
from terminal.terminal_customer import EpicTerminalCustomer
from views.customer_view import CustomerView
from views.user_view import UserView
from controllers.epic_controller import EpicDatabase
from controllers.session import create_engine, sessionmaker


@pytest.fixture(scope='module')
def test_session():
    # Crée une instance d'EpicDatabase avec les arguments requis
    db = EpicDatabase(database='app_db', host='localhost', user='mcourte', password='your_password')
    # Crée un moteur et une session SQLAlchemy pour les tests
    engine = create_engine(db.get_engine_url())
    Session = sessionmaker(bind=engine)
    session = Session()

    # Supprimer l'utilisateur spécifique s'il existe
    user_to_delete = session.query(EpicUser).filter_by(username='jdoe').first()
    if user_to_delete:
        session.delete(user_to_delete)
        session.commit()
    user_to_delete = session.query(EpicUser).filter_by(username='cdoe').first()
    if user_to_delete:
        session.delete(user_to_delete)
        session.commit()
    user_to_delete = session.query(EpicUser).filter_by(username='jbeam').first()
    if user_to_delete:
        session.delete(user_to_delete)
        session.commit()
    user_to_delete = session.query(EpicUser).filter_by(username='nuser').first()
    if user_to_delete:
        session.delete(user_to_delete)
        session.commit()

    yield session

    session.close()


@pytest.fixture
def epic_database():
    # Remplacez les arguments par ceux de votre configuration de base de données
    db = EpicDatabase(database='app_db', host='localhost', user='mcourte', password='your_password')
    yield db


@pytest.fixture
def current_user(test_session):
    current_user = test_session.query(EpicUser).filter_by(username="mcourte").first()
    return current_user


@pytest.fixture
def setup_customer_terminal(epic_database, test_session, current_user):
    return EpicTerminalCustomer(epic_database, test_session, current_user)


def test_list_of_customers(setup_customer_terminal, test_session, mocker):
    # Création de clients dans la base de données
    customer1 = Customer(customer_id=1, first_name="John", last_name="Doe",
                         email="jd@gmail.com", phone="000000000000", company_name="Legendre")
    customer2 = Customer(customer_id=2, first_name="Jane", last_name="Smith",
                         email="js@gmail.com", phone="000000000000", company_name="Cordee")
    test_session.add_all([customer1, customer2])
    test_session.commit()

    # Mock pour l'affichage des clients
    mocker.patch.object(CustomerView, 'display_list_customers', return_value=None)

    # Appel de la méthode à tester
    setup_customer_terminal.list_of_customers(test_session)

    # Vérification que les clients sont listés
    customers = test_session.query(Customer).all()
    assert len(customers) == 2


def test_update_customer_commercial(setup_customer_terminal, test_session, mocker):
    # Création d'un client sans commercial et d'un commercial
    customer = Customer(customer_id=1, first_name="John", last_name="Doe", commercial_id=None)
    commercial = EpicUser(epicuser_id=2, username="com_user", role="COM")
    test_session.add_all([customer, commercial])
    test_session.commit()

    # Mock des sélections de client et de commercial
    mocker.patch.object(CustomerView, 'prompt_client', return_value=customer.customer_id)
    mocker.patch.object(UserView, 'prompt_commercial', return_value=commercial.username)

    # Appel de la méthode à tester
    setup_customer_terminal.update_customer_commercial(test_session)

    # Vérification que le commercial a bien été attribué au client
    updated_customer = test_session.query(Customer).filter_by(customer_id=1).first()
    assert updated_customer.commercial_id == commercial.epicuser_id


def test_create_customer_as_commercial(setup_customer_terminal, test_session, mocker):
    # Simulation d'un utilisateur Commercial
    current_user = Commercial(epicuser_id=1, username="com_user", role="COM")
    setup_customer_terminal.current_user = current_user

    # Mock pour la saisie des données du client
    customer_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com"
    }
    mocker.patch.object(CustomerView, 'prompt_data_customer', return_value=customer_data)

    # Appel de la méthode à tester
    setup_customer_terminal.create_customer(test_session)

    # Vérification que le client a été créé
    created_customer = test_session.query(Customer).filter_by(first_name="John", last_name="Doe").first()
    assert created_customer is not None
    assert created_customer.commercial_id == current_user.epicuser_id


def test_update_customer(setup_customer_terminal, test_session, mocker):
    # Création d'un client associé à un commercial
    commercial = Commercial(epicuser_id=1, username="com_user", role="COM")
    customer = Customer(customer_id=1, first_name="John", last_name="Doe", commercial_id=commercial.epicuser_id)
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


def test_add_customer_commercial(setup_customer_terminal, test_session, mocker):
    # Création d'un client sans commercial et d'un commercial
    customer = Customer(customer_id=1, first_name="John", last_name="Doe", commercial_id=None)
    commercial = EpicUser(epicuser_id=2, username="com_user", role="COM")
    test_session.add_all([customer, commercial])
    test_session.commit()

    # Mock pour sélectionner le commercial
    mocker.patch.object(UserView, 'prompt_commercial', return_value=commercial.username)

    # Appel de la méthode à tester
    setup_customer_terminal.add_customer_commercial(test_session, customer)

    # Vérification que le commercial a bien été attribué au client
    updated_customer = test_session.query(Customer).filter_by(customer_id=1).first()
    assert updated_customer.commercial_id == commercial.epicuser_id
