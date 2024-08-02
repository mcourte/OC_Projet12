import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

# Importez les fonctions depuis server.py
from controllers import user_controller
from models import user, event,  contract, customer
from config import Base


@pytest.fixture(scope='function')
def init_db():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope='function')
def session(init_db):
    Session = sessionmaker(bind=init_db)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def user_controller_session(session):
    return user_controller.UserController(session)


def test_create_user_valid_role(user_controller_session):
    first_name = "Romain"
    last_name = "Martin"
    role = "com"
    password = "password123"
    user.User.generate_unique_username = lambda session, first, last: f"{first}.{last}".lower()
    try:
        user_controller_session.create_user(first_name, last_name, role, password)
        assert True
    except Exception as e:
        pytest.fail(f"Exception inattendue : {e}")


def test_create_user_invalid_role(user_controller_session):
    first_name = "Romain"
    last_name = "Martin"
    role = "commercial"
    password = "password123"
    with pytest.raises(ValueError, match=f"Rôle invalide, erreur: {role}"):
        user_controller_session.create_user(first_name, last_name, role, password)


def test_generate_username(user_controller_session):
    first_name = "Romain"
    last_name = "Martin"
    role = "com"
    password = "password123"
    user.User.generate_unique_username = lambda session, first, last: f"{first}.{last}".lower()
    try:
        user_controller_session.create_user(first_name, last_name, role, password)
        assert True
    except Exception as e:
        pytest.fail(f"Exception inattendue : {e}")


def test_create_user_attributes(user_controller_session):
    first_name = "Romain"
    last_name = "Martin"
    role = "com"
    password = "password123"

    user_controller_session.create_user(first_name, last_name, role, password)

    created_users = user_controller_session.get_users()
    print(f"Utilisateurs créés : {[user.username for user in created_users]}")

    assert len(created_users) > 0, "Aucun utilisateur créé"
    created_user = created_users[0]
    assert created_user.first_name == first_name
    assert created_user.last_name == last_name
    assert created_user.role == user.Role.COM
    assert created_user.check_password(password)


def test_generate_unique_username(session):
    first_name = "Romain"
    last_name = "Martin"
    username = user.User.generate_unique_username(session, first_name, last_name)
    assert username == f"{first_name}.{last_name}".lower()


def test_generate_unique_email(session):
    username = "rmartin"
    email = user.User.generate_unique_email(session, username)
    assert email == f"{username}@epic.com"


def test_set_password(session):
    user_password = user.User(
        first_name="Romain",
        last_name="Martin",
        username="romain.martin",
        role=user.Role.COM,
        password="initial_password",
        email="rmartin@epic.com"
    )
    user_password.set_password("password123")
    assert user_password.check_password("password123") is True


def test_create_user_role_assignment(user_controller_session):
    first_name = "Romain"
    last_name = "Martin"
    role = "ges"
    password = "password123"

    user_controller_session.create_user(first_name, last_name, role, password)
    created_users = user_controller_session.get_users()

    print(f"Utilisateurs créés : {[user.username for user in created_users]}")

    assert len(created_users) > 0, "Aucun utilisateur créé"
    created_user = created_users[0]
    assert created_user.role == user.Role.GES
