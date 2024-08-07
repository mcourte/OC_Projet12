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
from models.user import User
from config import Base
from permissions import Role, role_permissions, Permission, has_permission
from controllers.user_controller import UserController


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
        username="auser",
        role=Role.ADM.value,
        password="password123",
        email="auser@epic.com"
    )
    session.add(admin_user)
    session.commit()
    return UserController(session, admin_user.user_id)


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
    with pytest.raises(ValueError, match=f"Invalid role: {role}"):
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
    created_user = created_users[1]
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
    role = 'GES'
    password = "password123"

    user_controller_session.create_user(first_name, last_name, role, password)
    created_users = user_controller_session.get_users()

    assert len(created_users) > 0, "Aucun utilisateur créé"
    created_user = created_users[-1]

    print(f"Created user role: {created_user.role}, expected role: {Role.GES}")
    assert created_user.role.value == role, f"Expected role value '{role}', but got '{created_user.role.value}'"


def test_create_user_permission(user_controller_session):
    first_name = "Romain"
    last_name = "Martin"
    role = Role.COM.value
    password = "password123"

    # Test avec un utilisateur ayant le rôle GES
    user_controller_session.role = Role.GES
    try:
        user_controller_session.create_user(first_name, last_name, role, password)
    except PermissionError:
        pytest.fail("PermissionError inattendue: l'utilisateur avec le rôle GES devrait pouvoir créer un utilisateur.")


def test_edit_user_permission(user_controller_session):
    first_name = "Romain"
    last_name = "Martin"
    role = Role.COM.value
    password = "password123"
    User.generate_unique_username = lambda session, first, last: f"{first[0]}{last}".lower()
    user_controller_session.create_user(first_name, last_name, role, password)
    first_name = "Joann"
    last_name = "Martine"
    role = Role.SUP.value
    password = "password1234"

    # Test avec un utilisateur ayant le rôle GES
    user_controller_session.role = Role.GES
    assert has_permission(user_controller_session.user_role, Permission.SORT_USER)
    try:
        user_controller_session.edit_user(first_name, last_name, role, password)
    except PermissionError:
        pytest.fail("PermissionError inattendue: l'utilisateur avec le rôle GES" +
                    "devrait pouvoir modifier un utilisateur.")
    # Test avec un utilisateur ayant le rôle SUP
    user_controller_session.role = Role.SUP
    try:
        user_controller_session.edit_user(first_name, last_name, role, password)
    except PermissionError:
        pytest.fail("Vous n'avez pas la permission pour modifier un utilisateur.")


def test_create_user_with_empty_first_name(user_controller_session):
    with pytest.raises(ValueError, match="Le prénom ne peut pas être nul."):
        user_controller_session.create_user("", "Martin", Role.COM.value, "password123")


def test_create_user_with_empty_last_name(user_controller_session):
    with pytest.raises(ValueError, match="Le nom ne peut pas être nul."):
        user_controller_session.create_user("Romain", "", Role.COM.value, "password123")


def test_create_user_with_empty_role(user_controller_session):
    with pytest.raises(ValueError, match="Le rôle ne peut pas être nul."):
        user_controller_session.create_user("Romain", "Martin", "", "password123")


def test_create_user_with_empty_password(user_controller_session):
    with pytest.raises(ValueError, match="Le mot de passe ne peut pas être nul."):
        user_controller_session.create_user("Romain", "Martin", Role.COM.value, "")


def test_role_based_permission_check(user_controller_session):
    # Créer un utilisateur par un utilisateur qui n'a pas la permission de DELETE_USER
    first_name = "Romain"
    last_name = "Martin"
    role = Role.COM.value
    password = "password123"
    User.generate_unique_username = lambda session, first, last: f"{first[0]}{last}".lower()
    user_controller_session.create_user(first_name, last_name, role, password)

    created_user = user_controller_session.get_users()[-1]

    # Changer la permission vers un rôle qui n'a pas l'autorisation de DELETE_USER
    user_controller_session.user_role = Role.COM
    with pytest.raises(PermissionError):
        user_controller_session.delete_user(created_user.user_id)


def test_edit_user_details(user_controller_session):
    first_name = "Romain"
    last_name = "Martin"
    role = Role.COM.value
    password = "password123"
    user_controller_session.create_user(first_name, last_name, role, password)

    created_user = user_controller_session.get_users()[-1]
    new_first_name = "Updated"
    new_last_name = "Name"
    new_role = Role.GES.value

    user_controller_session.edit_user(created_user.user_id, new_first_name, new_last_name, new_role)
    assert user_controller_session.user_role in [Role.ADM, Role.GES], "L'utilisateur n'a pas la permission de modifier les utilisateurs."
    updated_user = user_controller_session.get_users()[-1]
    assert updated_user.first_name == new_first_name
    assert updated_user.last_name == new_last_name
    assert updated_user.role == new_role


def test_sort_users_by_role(user_controller_session):
    user_controller_session.create_user("Alice", "Admin", Role.ADM.value, "password123")
    user_controller_session.create_user("Bob", "Manager", Role.GES.value, "password123")
    user_controller_session.create_user("Charlie", "User", Role.COM.value, "password123")
    assert user_controller_session.user_role in [Role.ADM, Role.GES], "L'utilisateur n'a pas la permission de trier les utilisateurs."

    sorted_users = user_controller_session.sort_users('role')
    roles = [user.role for user in sorted_users]
    assert roles == sorted(roles), "User sont triés par rôle"


def test_get_all_users(user_controller_session):
    user_controller_session.create_user("Romain", "Martin", Role.COM.value, "password123")
    user_controller_session.create_user("John", "Doe", Role.GES.value, "password123")
    assert user_controller_session.user_role in [Role.ADM, Role.GES, Role.COM, Role.SUP], "L'utilisateur n'a pas la permission de trier les utilisateurs."

    users = user_controller_session.get_all_users()
    assert len(users) > 0, "Aucun user n'a été trouvé"
    assert all(isinstance(user, User) for user in users), "Les objets renvoyés ne sont pas des User"


def test_role_permission_mapping():
    assert Role.ADM in role_permissions, "Admin role is missing in role permissions"
    assert Permission.CREATE_USER in role_permissions[Role.ADM], "Admin role does not have create user permission"


def test_delete_user_permission(user_controller_session):
    # Create a user with GES role
    first_name = "Romain"
    last_name = "Martin"
    role = Role.GES.value
    password = "password123"
    user_controller_session.create_user(first_name, last_name, role, password)

    # Retrouver l'ID de l'utilisateur crée
    created_user = user_controller_session.get_users()[-1]
    assert user_controller_session.user_role == Role.ADM, "L'utilisateur n'a pas la permission de supprimer un User."
    # Essayer de supprimer l'utilisateur
    try:
        user_controller_session.delete_user(created_user.user_id)
    except PermissionError:
        pytest.fail("PermissionError inattendue: l'utilisateur avec le rôle ADM" +
                    "devrait pouvoir supprimer un utilisateur.")

    # Verifie que l'user a été supprimé
    remaining_users = user_controller_session.get_users()
    assert created_user not in remaining_users, "L'utilisateur n'a pas été supprimé"
