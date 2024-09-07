from unittest.mock import MagicMock, patch
import sys
import os
import datetime
import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the root directory to PYTHONPATH
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))
sys.path.insert(0, parent_dir)

# Import the necessary controllers
from controllers import user_controller, contract_controller, epic_controller, event_controller, customer_controller
from config_init import Base, SECRET_KEY

# Setup SQLAlchemy in-memory database for testing
engine = create_engine('sqlite:///:memory:', echo=False)
Session = sessionmaker(bind=engine)


def setup_in_memory_database():
    """Initialise une base de données en mémoire pour les tests."""
    Base.metadata.create_all(engine)
    return Session()


# Patch to disable permission checks for testing
def disable_permissions():
    patch('controllers.decorator.requires_roles', lambda *args: lambda x: x).start()
    patch('controllers.decorator.is_authenticated', lambda x: True).start()
    patch('controllers.decorator.load_session', lambda *args: 'fake_token').start()


# Mock controllers with valid SQLAlchemy session and view
def new_mock_main_controller():
    mock_session = MagicMock()
    mock_console = MagicMock()
    mock_user_controller = MagicMock()
    mock_customer_controller = MagicMock()
    mock_contract_controller = MagicMock()
    mock_event_controller = MagicMock()

    mock_main_controller = epic_controller.EpicBase(
        session=mock_session, console=mock_console
    )
    mock_main_controller.user_controller = mock_user_controller
    mock_main_controller.customer_controller = mock_customer_controller
    mock_main_controller.contract_controller = mock_contract_controller
    mock_main_controller.event_controller = mock_event_controller

    mock_main_controller.view = MagicMock()
    return mock_main_controller


def generate_valid_token(secret_key, user, expiration_hours=24):
    """
    Génère un token JWT valide pour les tests.
    """
    payload = {
        'username': user,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=expiration_hours),
        'role': 'Admin',
        'iat': datetime.datetime.utcnow(),
    }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token


def new_mock_user_controller(salt="test_salt", secret_key=SECRET_KEY):
    session = setup_in_memory_database()
    mock_view = MagicMock()

    mock_user_controller = user_controller.EpicUserBase(
        session=session, view=mock_view, salt=salt, secret_key=secret_key
    )
    return mock_user_controller


def new_mock_customer_controller():
    session = setup_in_memory_database()
    mock_view = MagicMock()

    mock_customer_controller = customer_controller.CustomerBase(
        session=session, view=mock_view
    )
    return mock_customer_controller


def new_mock_contract_controller():
    session = setup_in_memory_database()
    mock_view = MagicMock()

    mock_contract_controller = contract_controller.ContractBase(
        session=session, view=mock_view
    )
    return mock_contract_controller


def new_mock_event_controller():
    session = setup_in_memory_database()
    mock_view = MagicMock()

    mock_event_controller = event_controller.EventBase(
        session=session, view=mock_view
    )
    return mock_event_controller


# Disable permissions globally for all tests
disable_permissions()
