import pytest
import jwt
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, scoped_session
import sys
import os
import json
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from models.entities import EpicUser, Base
from controllers.customer_controller import CustomerBase
from config import SECRET_KEY


def generate_token(payload):
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


@pytest.fixture(scope='session')
def engine():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope='function')
def session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session_factory = sessionmaker(bind=connection)
    session = scoped_session(session_factory)
    yield session
    session.remove()
    transaction.rollback()
    connection.close()


@pytest.fixture
def login_user(session):
    admin_user = EpicUser(
        first_name="Admin",
        last_name="Test",
        username="atest",
        role="ADM",
        password="password",
        email="atest@epic.com",
        epicuser_id="18"
    )
    admin_user.set_password("password")
    session.add(admin_user)
    session.commit()
    yield admin_user


@pytest.fixture
def valid_token():
    return generate_token({"epicuser_id": 18, "role": "ADM"})


@pytest.fixture
def expired_token():
    return generate_token({"epicuser_id": 18, "role": "ADM", "exp": 0})


@pytest.fixture
def invalid_token():
    return "thisisnotavalidtoken"


@pytest.fixture(scope='session')
def create_session_file():
    token = jwt.encode({"epicuser_id": 18, "role": "ADM"}, SECRET_KEY, algorithm='HS256')
    with open('session.json', 'w') as f:
        json.dump({'token': token}, f)
    yield
    import os
    if os.path.exists('session.json'):
        os.remove('session.json')


@pytest.fixture(scope='function')
def session_with_token(create_session_file, session):
    return session


def test_database_structure(session):
    inspector = inspect(session.bind)
    tables = inspector.get_table_names()
    print("Tables in the database:", tables)
    for table_name in tables:
        columns = inspector.get_columns(table_name)
        print(f"Columns in {table_name}:", [column['name'] for column in columns])


@pytest.fixture
def unique_username():
    return lambda first_name, last_name: f"{first_name[0]}{last_name}"


@pytest.fixture
def unique_email():
    return lambda first_name, last_name: f"{first_name[0]}{last_name}@epic.com"


def test_create_customer(session, login_user):
    customer_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'johndoe@example.com',
        'phone': '1234567890',
        'company_name': 'Doe Inc.',
        'commercial_id': login_user.epicuser_id
    }
    customer_controller = CustomerBase(session)
    customer = customer_controller.create_customer(customer_data)

    assert customer.customer_id is not None
    assert customer.email == 'johndoe@example.com'


def test_get_customer(session, login_user):
    customer_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'johndoe@example.com',
        'phone': '1234567890',
        'company_name': 'Doe Inc.',
        'commercial_id': login_user.epicuser_id
    }
    customer_controller = CustomerBase(session)
    created_customer = customer_controller.create_customer(customer_data)

    customer = customer_controller.get_customer(created_customer.customer_id)

    assert customer is not None
    assert customer.first_name == 'John'


def test_update_customer(session, login_user):

    customer_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'johndoe@example.com',
        'phone': '1234567890',
        'company_name': 'Doe Inc.',
        'commercial_id': login_user.epicuser_id
    }
    customer_controller = CustomerBase(session)
    created_customer = customer_controller.create_customer(customer_data)

    update_data = {
        'first_name': 'Jane',
        'last_name': 'Doe'
    }
    customer_controller.update_customer(created_customer.customer_id, update_data)

    updated_customer = customer_controller.get_customer(created_customer.customer_id)

    assert updated_customer.first_name == 'Jane'


def test_find_without_contract(session, login_user):
    customer_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'johndoe@example.com',
        'phone': '1234567890',
        'company_name': 'Doe Inc.',
        'commercial_id': login_user.epicuser_id
    }
    customer_controller = CustomerBase(session)
    customer_controller.create_customer(customer_data)

    customers_without_contract = customer_controller.find_without_contract()
    assert len(customers_without_contract) > 0
