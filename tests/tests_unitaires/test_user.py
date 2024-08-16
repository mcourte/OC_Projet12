import pytest
from sqlalchemy import inspect
import os
import sys
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)
print(parent_dir)
from models.entities import EpicUser
from controllers.user_controller import EpicUserBase


@pytest.fixture
def user_controller_session(session):
    admin_user = EpicUser(
        first_name="Admin",
        last_name="User",
        username="auser",
        role="ADM",
        password="password123",
        email="auser@epic.com"
    )
    session.add(admin_user)
    session.commit()
    return EpicUserBase(session)


@pytest.fixture
def unique_username():
    return lambda first_name, last_name: f"{first_name[0]}{last_name}"


@pytest.fixture
def unique_email():
    return lambda first_name, last_name: f"{first_name[0]}{last_name}@epic.com"


def test_database_structure(session):
    inspector = inspect(session.bind)
    tables = inspector.get_table_names()
    print("Tables dans la base de données :", tables)
    for table_name in tables:
        columns = inspector.get_columns(table_name)
        print(f"Colonnes dans {table_name} :", [column['name'] for column in columns])


def test_create_user(session, unique_username, unique_email):
    epic_user_base = EpicUserBase(session)

    username = unique_username("David", "Courté")
    email = unique_email("David", "Courté")

    data = {
        "first_name": "David",
        "last_name": "Courté",
        "username": username,
        "password": "password",
        "role": "Commercial",
        "email": email
    }
    user = epic_user_base.create_user(data)

    assert user is not None
    assert user.username == username
    assert user.first_name == "David"
    assert user.last_name == "Courté"
    assert user.check_password("password") is True
    assert user.role == 'COM'


def test_create_user_duplicate_username(session, unique_username, unique_email):
    epic_user_base = EpicUserBase(session)

    username = unique_username("Pauline", "Legrand")
    email = unique_email("Pauline", "Legrand")

    data = {
        "first_name": "Pauline",
        "last_name": "Legrand",
        "username": username,
        "password": "password",
        "role": "Admin",
        "email": email
    }
    epic_user_base.create_user(data)

    with pytest.raises(ValueError):
        epic_user_base.create_user(data)  # Essayer de créer un utilisateur avec le même nom d'utilisateur

    users = session.query(EpicUser).filter_by(username=username).all()
    assert len(users) == 1


def test_add_user_commercial(session, unique_username, unique_email):
    epic_user_base = EpicUserBase(session)
    username = unique_username("John", "Doe")
    email = unique_email("John", "Doe")

    data = {
        "first_name": "John",
        "last_name": "Doe",
        "username": username,
        "password": "correctpassword",
        "role": "Commercial",
        "email": email
    }
    epic_user_base.create_user(data)

    user = epic_user_base.get_user(username)
    assert user is not None
    assert user.username == username
    assert user.role == "COM"


def test_add_user_support(session, unique_username, unique_email):
    epic_user_base = EpicUserBase(session)
    username = unique_username("Pauline", "Bellec")
    email = unique_email("Pauline", "Bellec")

    data = {
        "first_name": "Pauline",
        "last_name": "Bellec",
        "username": username,
        "password": "correctpassword",
        "role": "Support",
        "email": email
    }
    epic_user_base.create_user(data)

    user = epic_user_base.get_user(username)
    assert user is not None
    assert user.username == username
    assert user.role == "SUP"


def test_add_user_invalid_role(session, unique_username, unique_email):
    epic_user_base = EpicUserBase(session)
    username = unique_username("Romain", "Martin")
    email = unique_email("Romain", "Martin")

    data = {
        "first_name": "Romain",
        "last_name": "Martin",
        "username": username,
        "password": "password",
        "role": "InvalidRole",
        "email": email
    }
    with pytest.raises(ValueError):
        epic_user_base.create_user(data)


def test_get_user(session, unique_username, unique_email):
    epic_user_base = EpicUserBase(session)

    users = epic_user_base.get_all_users()
    init_len = len(users)

    username1 = unique_username("Mickaël", "Courté")
    email1 = unique_email("Mickaël", "Courté")
    username2 = unique_username("Maël", "Inizan")
    email2 = unique_email("Maël", "Inizan")

    data1 = {
        "first_name": "Mickaël",
        "last_name": "Courté",
        "username": username1,
        "password": "password",
        "role": "Commercial",
        "email": email1
    }
    data2 = {
        "first_name": "Maël",
        "last_name": "Inizan",
        "username": username2,
        "password": "password",
        "role": "Support",
        "email": email2
    }
    epic_user_base.create_user(data1)
    epic_user_base.create_user(data2)

    users = epic_user_base.get_all_users()
    assert len(users) == init_len + 2
    assert users[-2].username in [username1, username2]
    assert users[-1].username in [username1, username2]


def test_get_roles():
    epic_user_base = EpicUserBase(None)
    roles = epic_user_base.get_roles()

    assert len(roles) == 4
    assert "Commercial" in roles
    assert "Gestion" in roles
    assert "Support" in roles
    assert "Admin" in roles


def test_get_rolecode():
    epic_user_base = EpicUserBase(None)

    assert epic_user_base.get_rolecode("Commercial") == "COM"
    assert epic_user_base.get_rolecode("Gestion") == "GES"
    assert epic_user_base.get_rolecode("Support") == "SUP"
    assert epic_user_base.get_rolecode("Admin") == "ADM"
    assert epic_user_base.get_rolecode("NonExistentRole") is None


def test_update_user_role(session, unique_username, unique_email):
    epic_user_base = EpicUserBase(session)
    username = unique_username("Test", "User")
    email = unique_email("Test", "User")

    data = {
        "first_name": "Test",
        "last_name": "User",
        "username": username,
        "password": "password",
        "role": "Commercial",
        "email": email
    }
    epic_user_base.create_user(data)

    epic_user_base.update_user(name=username, role="Support")

    user = session.query(EpicUser).filter_by(username=username).first()
    assert user is not None
    assert user.role == 'SUP'


def test_update_user_password(session, unique_username, unique_email):
    epic_user_base = EpicUserBase(session)
    username = unique_username("No", "Idea")
    email = unique_email("No", "Idea")

    data = {
        "first_name": "No",
        "last_name": "Idea",
        "username": username,
        "password": "password",
        "role": "Commercial",
        "email": email
    }
    epic_user_base.create_user(data)

    epic_user_base.update_user(name=username, password="newpassword")

    user = session.query(EpicUser).filter_by(username=username).first()
    assert user is not None
    assert user.check_password("newpassword") is True


def test_getall_commercials(session, unique_username, unique_email):
    epic_user_base = EpicUserBase(session)
    initial_count = len(epic_user_base.get_commercials())

    data1 = {
        "first_name": "Pouf",
        "last_name": "User",
        "username": unique_username("Pouf", "User"),
        "password": "password",
        "role": "Commercial",
        "email": unique_email("Pouf", "User")
    }
    data2 = {
        "first_name": "Lolilol",
        "last_name": "User",
        "username": unique_username("Lolilol", "User"),
        "password": "password",
        "role": "Commercial",
        "email": unique_email("Lolilol", "User")
    }
    epic_user_base.create_user(data1)
    epic_user_base.create_user(data2)

    commercials = epic_user_base.get_commercials()
    assert len(commercials) == initial_count + 2


def test_getall_supports(session, unique_username, unique_email):
    epic_user_base = EpicUserBase(session)

    supports = epic_user_base.get_supports()
    init_len = len(supports)

    username1 = unique_username("Brad", "Pitt")
    email1 = unique_email("Brad", "Pitt")
    username2 = unique_username("Morgan", "Freeman")
    email2 = unique_email("Morgan", "Freeman")

    data1 = {
        "first_name": "Brad",
        "last_name": "Pitt",
        "username": username1,
        "password": "password",
        "role": "Support",
        "email": email1
    }
    data2 = {
        "first_name": "Morgan",
        "last_name": "Freeman",
        "username": username2,
        "password": "password",
        "role": "Support",
        "email": email2
    }
    epic_user_base.create_user(data1)
    epic_user_base.create_user(data2)

    supports = epic_user_base.get_supports()
    assert len(supports) == init_len + 2
    assert all(user.role == 'SUP' for user in supports)


def test_getall_gestion(session, unique_username, unique_email):
    epic_user_base = EpicUserBase(session)

    gestions = epic_user_base.get_gestions()
    init_len = len(gestions)

    username1 = unique_username("Angelina", "Jolie")
    email1 = unique_email("Angelina", "Jolie")
    username2 = unique_username("Nathalie", "Portman")
    email2 = unique_email("Nathalie", "Portman")

    data1 = {
        "first_name": "Angelina",
        "last_name": "Jolie",
        "username": username1,
        "password": "password",
        "role": "Gestion",
        "email": email1
    }
    data2 = {
        "first_name": "Nathalie",
        "last_name": "Portman",
        "username": username2,
        "password": "password",
        "role": "Gestion",
        "email": email2
    }
    epic_user_base.create_user(data1)
    epic_user_base.create_user(data2)

    gestions = epic_user_base.get_gestions()

    assert len(gestions) == init_len + 2
    assert all(user.role == 'GES' for user in gestions)
