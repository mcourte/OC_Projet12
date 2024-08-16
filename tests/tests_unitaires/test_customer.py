import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)
from tests.conftest import Base
from controllers.customer_controller import CustomerBase


@pytest.fixture(scope='module')
def session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


def test_create_customer(session):
    customer_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'johndoe@example.com',
        'phone': '1234567890',
        'company_name': 'Doe Inc.',
        'commercial_id': None
    }
    customer_controller = CustomerBase(session)
    customer = customer_controller.create_customer(customer_data)

    assert customer.customer_id is not None
    assert customer.email == 'johndoe@example.com'


def test_get_customer(session):
    customer_controller = CustomerBase(session)
    customer = customer_controller.get_customer(1)

    assert customer is not None
    assert customer.first_name == 'John'


def test_update_customer(session):
    customer_controller = CustomerBase(session)
    update_data = {
        'first_name': 'Jane',
        'last_name': 'Doe'
    }
    customer_controller.update_customer(1, update_data)
    customer = customer_controller.get_customer(1)

    assert customer.first_name == 'Jane'
