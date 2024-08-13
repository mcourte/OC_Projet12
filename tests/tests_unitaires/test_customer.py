import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.entities import Base
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


def test_delete_customer(session):
    customer_controller = CustomerBase(session)
    customer_controller.delete_customer(1)
    customer = customer_controller.get_customer(1)

    assert customer is None
