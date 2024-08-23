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

from controllers.contract_controller import ContractBase
from models.entities import EpicUser, Base, Contract, Paiement
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
    token = jwt.encode({"epicuser_id": 15, "role": "ADM"}, SECRET_KEY, algorithm='HS256')
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


@pytest.fixture(scope='function')
def contract_base(session):
    return ContractBase(session)


@pytest.fixture
def sample_contract():
    return Contract(
        description="Test Contract",
        total_amount=1000,
        remaining_amount=500,
        state='C',
        customer_id=1,
        paiement_state='N',
        contract_id=1
    )


def test_create_contract_success(contract_base, session):
    data = {
        'description': 'New Contract',
        'total_amount': 1000,
        'remaining_amount': 500,
        'state': 'C',
        'customer_id': 1,
        'paiement_state': 'N'
    }
    contract = contract_base.create_contract(data)
    assert contract.description == 'New Contract'
    assert contract.total_amount == 1000
    assert contract.remaining_amount == 500
    assert contract.state == 'C'
    assert contract.customer_id == 1
    assert contract.paiement_state == 'N'


def test_get_contract_success(contract_base, session, sample_contract):
    session.add(sample_contract)
    session.commit()
    result = contract_base.get_contract(sample_contract.contract_id)
    assert result == sample_contract


def test_get_contract_not_found(contract_base, session):
    result = contract_base.get_contract(999)
    assert result is None


def test_get_all_contracts(contract_base, session, sample_contract):
    session.add(sample_contract)
    session.commit()
    contracts = contract_base.get_all_contracts()
    assert len(contracts) == 1
    assert contracts[0] == sample_contract


def test_update_contract_success(contract_base, session, sample_contract):
    session.add(sample_contract)
    session.commit()
    data = {'description': 'Nouvelle Description'}
    contract_base.update_contract(sample_contract.contract_id, data)
    updated_contract = session.query(Contract).get(sample_contract.contract_id)
    assert updated_contract.description == 'Nouvelle Description'


def test_update_contract_not_found(contract_base, session):
    with pytest.raises(ValueError):
        contract_base.update_contract(999, {'description': 'Does not exist'})


def test_find_by_customer_success(contract_base, session, sample_contract):
    session.add(sample_contract)
    session.commit()
    contracts = contract_base.find_by_customer(1)
    assert len(contracts) == 1
    assert contracts[0] == sample_contract


def test_find_by_customer_not_found(contract_base, session):
    contracts = contract_base.find_by_customer(999)
    assert len(contracts) == 0


def test_find_by_state_success(contract_base, session, sample_contract):
    session.add(sample_contract)
    session.commit()
    contracts = contract_base.find_by_state('C')
    assert len(contracts) == 1
    assert contracts[0] == sample_contract


def test_find_by_state_not_found(contract_base, session):
    contracts = contract_base.find_by_state('X')
    assert len(contracts) == 0


def test_find_by_paiement_state_success(contract_base, session, sample_contract):
    session.add(sample_contract)
    session.commit()
    contracts = contract_base.find_by_paiement_state('N')
    assert len(contracts) == 1
    assert contracts[0] == sample_contract


def test_find_by_paiement_state_not_found(contract_base, session):
    contracts = contract_base.find_by_paiement_state('X')
    assert len(contracts) == 0


def test_add_paiement_success(contract_base, session, sample_contract):
    session.add(sample_contract)
    session.commit()
    data = {'paiement_id': 'PAY123', 'amount': 500}
    contract_base.add_paiement(sample_contract.contract_id, data)
    paiements = session.query(Paiement).first()
    assert paiements.paiement_id == 'PAY123'
    assert paiements.amount == 500


def test_add_paiement_amount_exceeds_remaining(contract_base, session, sample_contract):
    session.add(sample_contract)
    session.commit()
    data = {'paiement_id': 'PAY123', 'amount': 600}
    with pytest.raises(ValueError, match="Le montant dépasse le restant dû"):
        contract_base.add_paiement(sample_contract.contract_id, data)


def test_signed_success(contract_base, session, sample_contract):
    session.add(sample_contract)
    session.commit()
    contract_base.signed(sample_contract.contract_id)
    updated_contract = session.query(Contract).get(sample_contract.contract_id)
    assert updated_contract.state == 'S'


def test_signed_contract_not_found(contract_base, session):
    with pytest.raises(ValueError, match="Aucun contrat trouvé avec la référence 999"):
        contract_base.signed(999)
