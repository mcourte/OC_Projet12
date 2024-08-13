import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.entities import Base
from controllers.contract_controller import ContractBase


@pytest.fixture(scope='module')
def session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


def test_create_contract(session):
    contract_data = {
        'description': 'Contract for Service',
        'total_amount': 1000.00,
        'remaining_amount': 500.00,
        'state': 'C',
        'customer_id': 1
    }
    contract_controller = ContractBase(session)
    contract = contract_controller.create_contract(contract_data)

    assert contract.contract_id is not None
    assert contract.description == 'Contract for Service'


def test_get_contract(session):
    contract_controller = ContractBase(session)
    contract = contract_controller.get_contract(1)

    assert contract is not None
    assert contract.total_amount == 1000.00


def test_update_contract(session):
    contract_controller = ContractBase(session)
    update_data = {
        'remaining_amount': 400.00
    }
    contract_controller.update_contract(1, update_data)
    contract = contract_controller.get_contract(1)

    assert contract.remaining_amount == 400.00


def test_delete_contract(session):
    contract_controller = ContractBase(session)
    contract_controller.delete_contract(1)
    contract = contract_controller.get_contract(1)

    assert contract is None
