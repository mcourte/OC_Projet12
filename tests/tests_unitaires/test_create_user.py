import os
import sys
import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

# Importez les fonctions depuis server.py
from controllers import user_controller
from models.user import User
from config import Base
from permissions import Role


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
    session.query(User).delete()  # Réinitialiser les utilisateurs
    yield session
    session.close()


@pytest.fixture
def user_controller_session(session):
    # Créer un utilisateur pour initialiser le UserController
    admin_user = User(
        first_name="Admin",
        last_name="User",
        username="admin.user",
        role="ADM",
        password="password123",
        email="admin.user@epic.com"
    )
    session.add(admin_user)
    session.commit()
    return user_controller.UserController(session, admin_user.user_id)


def test_database_structure(session):
    inspector = inspect(session.bind)
    tables = inspector.get_table_names()
    print("Tables dans la base de données :", tables)
    for table_name in tables:
        columns = inspector.get_columns(table_name)
        print(f"Colonnes dans {table_name} :", [column['name'] for column in columns])


def test_create_user_valid_role(user_controller_session):
    first_name = "Romain"
    last_name = "Martin"
    role = Role.COM.value
    password = "password123"
    User.generate_unique_username = lambda session, first, last: f"{first}.{last}".lower()
    try:
        user_controller_session.create_user(first_name, last_name, role, password)
        assert True
    except Exception as e:
        pytest.fail(f"Exception inattendue : {e}")


def test_create_user_invalid_role(user_controller_session):
    first_name = "Romain"
    last_name = "Martin"
    role = "invalid_role"
    password = "password123"
    with pytest.raises(ValueError, match=f"Rôle invalide, erreur: {role}"):
        user_controller_session.create_user(first_name, last_name, role, password)


def test_generate_username(user_controller_session):
    first_name = "Romain"
    last_name = "Martin"
    role = Role.COM.value
    password = "password123"
    User.generate_unique_username = lambda session, first, last: f"{first[0]}{last}".lower()
    try:
        user_controller_session.create_user(first_name, last_name, role, password)
        assert True
    except Exception as e:
        pytest.fail(f"Exception inattendue : {e}")


def test_create_user_attributes(user_controller_session):
    first_name = "Romain"
    last_name = "Martin"
    role = Role.ADM.value
    password = "password123"

    user_controller_session.create_user(first_name, last_name, role, password)
    created_users = user_controller_session.get_users()

    assert len(created_users) > 0, "Aucun utilisateur créé"
    created_user = created_users[0]
    assert created_user.first_name == first_name
    assert created_user.last_name == last_name


def test_generate_unique_username(session):
    first_name = "Romain"
    last_name = "Martin"
    username = User.generate_unique_username(session, first_name, last_name)
    assert username == f"{first_name[0].lower()}{last_name.lower()}"


def test_generate_unique_email(session):
    username = "rmartin"
    email = User.generate_unique_email(session, username)
    assert email == f"{username}@epic.com"


def test_set_password(session):
    user_password = User(
        first_name="Romain",
        last_name="Martin",
        username="romain.martin",
        role=Role.COM.value,
        password="initial_password",
        email="rmartin@epic.com"
    )
    user_password.set_password("password123")
    assert user_password.check_password("password123") is True


def test_create_user_role_assignment(user_controller_session):
    first_name = "Romain"
    last_name = "Martin"
    role = Role.GES.value
    password = "password123"

    user_controller_session.create_user(first_name, last_name, role, password)
    created_users = user_controller_session.get_users()

    assert len(created_users) > 0, "Aucun utilisateur créé"
    created_user = created_users[0]
    assert created_user.role == Role.GES


def test_create_user_permission(user_controller_session):
    first_name = "Romain"
    last_name = "Martin"
    role = Role.COM.value
    password = "password123"

    # Test avec un utilisateur ayant le rôle GES
    user_controller_session.user_role = Role.GES
    try:
        user_controller_session.create_user(first_name, last_name, role, password)
    except PermissionError:
        pytest.fail("PermissionError inattendue: l'utilisateur avec le rôle GES devrait pouvoir créer un utilisateur.")


def test_sort_users(user_controller_session):
    # Créer quelques utilisateurs
    user_controller_session.create_user("Admin", "User", Role.ADM.value, "password123")
    user_controller_session.create_user("John", "Doe", Role.COM.value, "password123")

    sorted_users = user_controller_session.sort_users('username')
    assert len(sorted_users) > 0, "La liste des utilisateurs triés est vide."

    # Vérifiez si les utilisateurs sont correctement triés
    assert sorted_users[0].username == "auser", "L'ordre de tri n'est pas correct"
