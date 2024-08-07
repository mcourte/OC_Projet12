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
from models.event import Event
from models.user import User
from config import Base
from permissions import Role, role_permissions, Permission, has_permission
from controllers.event_controller import EventController


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
    # Créer un utilisateur pour initialiser le EventController
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
    return EventController(session, admin_user.user_id)


def test_database_structure(session):
    inspector = inspect(session.bind)
    tables = inspector.get_table_names()
    print("Tables dans la base de données :", tables)
    for table_name in tables:
        columns = inspector.get_columns(table_name)
        print(f"Colonnes dans {table_name} :", [column['name'] for column in columns])


def test_create_event(user_controller_session):
    name = "Test"
    start_date = 10/12/2024
    end_date = 12/10/2024
    location = "Rennes"
    attendees = 140
    notes = "blablabla"
    try:
        user_controller_session.create_event(name, start_date, end_date, location, attendees, notes)
        assert True
    except Exception as e:
        pytest.fail(f"Exception inattendue : {e}")


def test_create_event_permission(user_controller_session):
    name = "Test"
    start_date = 10/12/2024
    end_date = 12/10/2024
    location = "Rennes"
    attendees = 140
    notes = "blablabla"

    # Test avec un utilisateur ayant le rôle COM
    user_controller_session.role = Role.COM
    try:
        user_controller_session.create_event(name, start_date, end_date, location, attendees, notes)
    except PermissionError:
        pytest.fail("PermissionError inattendue: l'utilisateur avec le rôle COM devrait pouvoir créer un Event")


def test_edit_event_permission(user_controller_session):
    name = "Test"
    start_date = 10/12/2024
    end_date = 12/10/2024
    location = "Rennes"
    attendees = 140
    notes = "blablabla"
    user_controller_session.create_event(name, start_date, end_date, location, attendees, notes)
    name = "Test- edit"
    start_date = 12/12/2024
    end_date = 20/10/2024
    location = "Douarnenez"
    attendees = 140
    notes = "blablabla"

    # Test avec un utilisateur ayant le rôle GES
    user_controller_session.role = Role.GES
    assert has_permission(user_controller_session.user_role, Permission.EDIT_EVENT)
    try:
        user_controller_session.edit_event(name, start_date, end_date, location, attendees, notes)
    except PermissionError:
        pytest.fail("PermissionError inattendue: l'utilisateur avec le rôle GES" +
                    "devrait pouvoir modifier un utilisateur.")
    # Test avec un utilisateur ayant le rôle SUP
    user_controller_session.role = Role.COM
    try:
        user_controller_session.edit_event(name, start_date, end_date, location, attendees, notes)
    except PermissionError:
        pytest.fail("Vous n'avez pas la permission pour modifier un utilisateur.")


def test_edit_user_details(user_controller_session):
    name = "Test"
    start_date = 10/12/2024
    end_date = 12/10/2024
    location = "Rennes"
    attendees = 140
    notes = "blablabla"
    user_controller_session.create_event(name, start_date, end_date, location, attendees, notes)
    created_event = user_controller_session.get_events()[-1]
    new_name = "Test- edit"
    new_start_date = 12/12/2024
    new_end_date = 20/10/2024

    user_controller_session.edit_user(created_event.event_id, new_name, new_start_date, new_end_date)
    assert user_controller_session.user_role in [Role.ADM, Role.GES], "L'utilisateur n'a pas la permission de modifier les utilisateurs."
    updated_event = user_controller_session.get_events()[-1]
    assert updated_event.name == new_name
    assert updated_event.stard_date == new_start_date
    assert updated_event.end_date == new_end_date


def test_get_all_events(user_controller_session):
    user_controller_session.create_event("Test", 12/10/2024, 15/10/2024, "Rennes", 140, "blabla")
    user_controller_session.create_event("Test-1", 20/10/2024, 25/10/2024, "Douarnenez", 80, "blabla-2")
    assert user_controller_session.user_role in [Role.ADM, Role.GES, Role.COM, Role.SUP], "L'utilisateur n'a pas la permission de trier les utilisateurs."

    events = user_controller_session.get_all_events()
    assert len(events) > 0, "Aucun user n'a été trouvé"
    assert all(isinstance(event, Event) for event in events), "Les objets renvoyés ne sont pas des User"


def test_role_permission_mapping():
    assert Role.ADM in role_permissions, "Admin role is missing in role permissions"
    assert Permission.CREATE_EVENT in role_permissions[Role.ADM], "Admin role does not have create user permission"
