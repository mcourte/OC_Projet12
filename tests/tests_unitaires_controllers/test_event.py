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
from config_init import SECRET_KEY


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
    token = jwt.encode(
        {"epicuser_id": 15, "role": "ADM", "exp": datetime.utcnow() + timedelta(hours=1)},
        SECRET_KEY,
        algorithm='HS256'
    )

    with open('session.json', 'w') as f:
        json.dump({'token': token}, f)

    yield token

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


def test_create_event(session):
    event_controller = EventBase(session)
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
    event = event_controller.create_event(create_data)
    assert event.title == 'Company Meeting'
    assert event.event_id is not None


def test_get_event(session):
    event_controller = EventBase(session)

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

    event = event_controller.get_event(created_event.event_id)

    assert event is not None
    assert event.title == 'Company Meeting'


def test_update_event(session):
    event_controller = EventBase(session)

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

    update_data = {
        'title': 'Updated Meeting',
        'date_started': datetime(2023, 1, 1, 10, 0, 0),
        'date_ended': datetime(2023, 1, 1, 12, 0, 0),
    }
    event_controller.update_event(created_event.event_id, update_data)

    updated_event = event_controller.get_event(created_event.event_id)

    assert updated_event.title == 'Updated Meeting'
