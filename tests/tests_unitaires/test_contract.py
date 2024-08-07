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
from models.contract import Contract
from models.user import User
from config import Base
from permissions import Role, role_permissions, Permission, has_permission
from controllers.contract_controller import ContractController


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
    return ContractController(session, admin_user.user_id)


def test_database_structure(session):
    inspector = inspect(session.bind)
    tables = inspector.get_table_names()
    print("Tables dans la base de données :", tables)
    for table_name in tables:
        columns = inspector.get_columns(table_name)
        print(f"Colonnes dans {table_name} :", [column['name'] for column in columns])


def test_create_contract(user_controller_session):
    total_amount = 15000
    remaining_amout = 4999
    is_signed = True

    try:
        user_controller_session.create_contract(total_amount, remaining_amout, is_signed)
        assert True
    except Exception as e:
        pytest.fail(f"Exception inattendue : {e}")


def test_create_contract_permission(user_controller_session):
    total_amount = 15000
    remaining_amout = 4999
    is_signed = True

    # Test avec un utilisateur ayant le rôle COM
    user_controller_session.role = Role.GES
    try:
        user_controller_session.create_contract(total_amount, remaining_amout, is_signed)
    except PermissionError:
        pytest.fail("PermissionError inattendue: l'utilisateur avec le rôle GES devrait pouvoir créer un Contract")


def test_edit_event_permission(user_controller_session):
    total_amount = 15000
    remaining_amout = 4999
    is_signed = True
    user_controller_session.create_contract(total_amount, remaining_amout, is_signed)

    new_total_amount = 16000
    new_remaining_amout = 6000
    new_is_signed = True

    # Test avec un utilisateur ayant le rôle GES
    user_controller_session.role = Role.GES
    assert has_permission(user_controller_session.user_role, Permission.CREATE_EVENT)
    try:
        user_controller_session.create_contract(new_total_amount, new_remaining_amout, new_is_signed)
    except PermissionError:
        pytest.fail("PermissionError inattendue: l'utilisateur avec le rôle GES" +
                    "devrait pouvoir modifier un contract.")
    # Test avec un utilisateur ayant le rôle COM
    user_controller_session.role = Role.SUP
    try:
        user_controller_session.create_contract(total_amount, remaining_amout, is_signed)
    except PermissionError:
        pytest.fail("Vous n'avez pas la permission pour modifier un contract.")


def test_get_all_contract(user_controller_session):
    user_controller_session.create_contract(15000, 6000, True)
    user_controller_session.create_contract(15000, 15000, False)
    assert user_controller_session.user_role in [Role.ADM, Role.GES, Role.COM, Role.SUP], "L'utilisateur n'a pas la permission de trier les utilisateurs."

    contracts = user_controller_session.get_all_contracts()
    assert len(contracts) > 0, "Aucun contract n'a été trouvé"
    assert all(isinstance(contract, Contract) for contract in contracts), "Les objets renvoyés ne sont pas des User"


def test_role_permission_mapping():
    assert Role.ADM in role_permissions, "Admin role is missing in role permissions"
    assert Permission.CREATE_CONTRACT in role_permissions[Role.ADM], "Admin role does not have create user permission"
