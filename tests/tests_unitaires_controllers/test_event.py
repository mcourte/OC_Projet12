import pytest
import jwt
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, scoped_session
import sys
import os
from datetime import datetime, timedelta
import json
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)
print(parent_dir)

from models.entities import EpicUser, Base
from controllers.event_controller import EventBase
from config import SECRET_KEY


def generate_token(payload):
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


@pytest.fixture(scope='session')
def engine():
    engine = create_engine('sqlite:///:memory:')  # Use an in-memory SQLite database for tests
    Base.metadata.create_all(engine)  # Create all tables
    yield engine
    Base.metadata.drop_all(engine)  # Clean up after tests


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
    """Fixture to login a user for authentication-dependent tests"""
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
    return generate_token({"epicuser_id": 18, "role": "ADM", "exp": 0})  # Expired token


@pytest.fixture
def invalid_token():
    return "thisisnotavalidtoken"


@pytest.fixture(scope='session')
def create_session_file():
    # Generate a token
    token = jwt.encode(
        {"epicuser_id": 15, "role": "ADM", "exp": datetime.utcnow() + timedelta(hours=1)},
        SECRET_KEY,
        algorithm='HS256'
    )

    # Write token to session.json
    with open('session.json', 'w') as f:
        json.dump({'token': token}, f)

    yield token

    # Cleanup
    import os
    if os.path.exists('session.json'):
        os.remove('session.json')


@pytest.fixture(scope='function')
def session_with_token(create_session_file, session):
    # Ensure that the session file is created before each test
    return session


# Example of a test using these fixtures
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


def test_create_event(session):
    event_controller = EventBase(session)
    create_data = {
        'title': 'Company Meeting',
        'date_started': datetime(2023, 1, 1, 10, 0, 0),
        'date_ended': datetime(2023, 1, 1, 12, 0, 0),
        'description': 'Annual meeting',
        'location': 'Conference Room',
        'attendees': 10,
        'report': 'Summary Report',  # Ensure report is not required
        'customer_id': None,
        'support_id': None,
        'contract_id': None
    }
    event = event_controller.create_event(create_data)
    assert event.title == 'Company Meeting'
    assert event.event_id is not None  # Ensure the event was created with an ID


def test_get_event(session):
    event_controller = EventBase(session)

    # Create an event first
    create_data = {
        'title': 'Company Meeting',
        'date_started': datetime(2023, 1, 1, 10, 0, 0),
        'date_ended': datetime(2023, 1, 1, 12, 0, 0),
        'description': 'Annual meeting',
        'location': 'Conference Room',
        'attendees': 10,
        'report': 'Summary Report',
        'customer_id': None,
        'support_id': None,
        'contract_id': None
    }
    created_event = event_controller.create_event(create_data)

    # Retrieve the event
    event = event_controller.get_event(created_event.event_id)

    assert event is not None
    assert event.title == 'Company Meeting'


def test_update_event(session):
    event_controller = EventBase(session)

    # Create an event first
    create_data = {
        'title': 'Company Meeting',
        'date_started': datetime(2023, 1, 1, 10, 0, 0),
        'date_ended': datetime(2023, 1, 1, 12, 0, 0),
        'description': 'Annual meeting',
        'location': 'Conference Room',
        'attendees': 10,
        'report': 'Summary Report',
        'customer_id': None,
        'support_id': None,
        'contract_id': None
    }
    created_event = event_controller.create_event(create_data)

    # Update the event
    update_data = {
        'title': 'Updated Meeting',
        'date_started': datetime(2023, 1, 1, 10, 0, 0),
        'date_ended': datetime(2023, 1, 1, 12, 0, 0),
    }
    event_controller.update_event(created_event.event_id, update_data)

    # Retrieve the updated event
    updated_event = event_controller.get_event(created_event.event_id)

    assert updated_event.title == 'Updated Meeting'
