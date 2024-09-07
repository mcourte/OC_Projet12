import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.entities import EpicUser, Base, Customer, Event, Contract
from datetime import datetime, timedelta


# Configuration pour les tests
@pytest.fixture(scope='module')
def test_session():
    engine = create_engine('sqlite:///:memory:')  # Utilisation d'une base de données en mémoire pour les tests
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    Base.metadata.drop_all(engine)


# Tests pour EpicUser
def test_create_epic_user(test_session):
    user = EpicUser(
        role='COM',
        first_name='John',
        last_name='Doe',
        username='jdoe',
        password='securepassword',
        email='jdoe@epic.com',
        state='A'
    )
    test_session.add(user)
    test_session.commit()

    assert user.epicuser_id is not None
    assert user.first_name == 'John'
    assert user.last_name == 'Doe'
    assert user.username == 'jdoe'
    assert user.email == 'jdoe@epic.com'
    assert user.state == 'A'


def test_generate_unique_username(test_session):
    EpicUser.generate_unique_username(test_session, 'Jane', 'Doe')
    user1 = EpicUser(username='jdoe')
    test_session.add(user1)
    test_session.commit()

    unique_username = EpicUser.generate_unique_username(test_session, 'John', 'Doe')
    assert unique_username != 'jdoe'


def test_generate_unique_email(test_session):
    EpicUser.generate_unique_email(test_session, 'jdoe')
    user1 = EpicUser(email='jdoe@example.com')
    test_session.add(user1)
    test_session.commit()

    unique_email = EpicUser.generate_unique_email(test_session, 'jdoe')
    assert unique_email != 'jdoe@example.com'


def test_set_password(test_session):
    user = EpicUser(username='jdoe')
    user.set_password('securepassword')
    test_session.add(user)
    test_session.commit()

    assert user.password is not None


def test_check_password_correct(test_session):
    user = EpicUser(username='jdoe')
    user.set_password('securepassword')
    test_session.add(user)
    test_session.commit()

    assert user.check_password('securepassword') is True


def test_check_password_incorrect(test_session):
    user = EpicUser(username='jdoe')
    user.set_password('securepassword')
    test_session.add(user)
    test_session.commit()

    assert user.check_password('wrongpassword') is False


def test_find_by_username(test_session):
    user = EpicUser(
        role='COM',
        first_name='John',
        last_name='Doe',
        username='jdoe',
        password='securepassword',
        email='jdoe@epic.com',
        state='A'
    )
    test_session.add(user)
    test_session.commit()

    found_user = EpicUser.find_by_username(test_session, 'jdoe')
    assert found_user is not None
    assert found_user.username == 'jdoe'


def test_update_role(test_session):
    user = EpicUser(
        role='COM',
        first_name='John',
        last_name='Doe',
        username='jdoe',
        password='securepassword',
        email='jdoe@epic.com',
        state='A'
    )
    test_session.add(user)
    test_session.commit()

    user.update_role('ADM')
    test_session.commit()

    assert user.role == 'ADM'


def test_set_inactive(test_session):
    user = EpicUser(
        role='COM',
        first_name='John',
        last_name='Doe',
        username='jdoe',
        password='securepassword',
        email='jdoe@epic.com',
        state='A'
    )
    test_session.add(user)
    test_session.commit()

    user.set_inactive()
    assert user.state == 'I'


def test_reassign_customers(test_session):
    user = EpicUser(
        role='COM',
        first_name='John',
        last_name='Doe',
        username='jdoe',
        password='securepassword',
        email='jdoe@epic.com',
        state='A'
    )
    test_session.add(user)
    test_session.commit()

    new_commercial = EpicUser(
        role='COM',
        first_name='Jane',
        last_name='Doe',
        username='jdoe1',
        password='securepassword',
        email='jdoe1@epic.com',
        state='A'
    )
    test_session.add(new_commercial)
    test_session.commit()

    # Assigner un client à l'utilisateur John
    customer = Customer(commercial_id=user.epicuser_id, first_name='Alice', last_name='Smith',
                        email='alice@example.com', phone='1234567890', company_name='Company A')
    test_session.add(customer)
    test_session.commit()

    user.reassign_customers()
    assert customer.commercial_id == new_commercial.epicuser_id


def test_notify_gestion(test_session, mocker):
    user = EpicUser(
        role='COM',
        first_name='John',
        last_name='Doe',
        username='jdoe',
        password='securepassword',
        email='jdoe@epic.com',
        state='A'
    )
    test_session.add(user)
    test_session.commit()

    mock_notify = mocker.patch.object(user, 'notify_gestion', autospec=True)
    user.notify_gestion("Test message")
    mock_notify.assert_called_once_with("Test message")


def test_create_epic_event(test_session):
    event = Event(
        title='Event 1',
        description='Description of Event 1',
        event_date=datetime.now(),
        customer_id=1,  # Assurez-vous que cet ID existe dans la base de données ou utilisez une autre méthode
        user_id=1       # Assurez-vous que cet ID existe dans la base de données ou utilisez une autre méthode
    )
    test_session.add(event)
    test_session.commit()
    assert event.event_id is not None
    assert event.title == 'Event 1'


def test_create_epic_contract(test_session):
    contract = Contract(
        title='Contract 1',
        description='Description of Contract 1',
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30),
        customer_id=1  # Assurez-vous que cet ID existe dans la base de données ou utilisez une autre méthode
    )
    test_session.add(contract)
    test_session.commit()
    assert contract.contract_id is not None
    assert contract.title == 'Contract 1'


def test_create_epic_customer(test_session):
    customer = Customer(
        first_name='Alice',
        last_name='Smith',
        email='alice@example.com',
        phone='1234567890',
        company_name='Company A',
        commercial_id=1  # Assurez-vous que cet ID existe dans la base de données ou utilisez une autre méthode
    )
    test_session.add(customer)
    test_session.commit()
    assert customer.customer_id is not None
    assert customer.email == 'alice@example.com'

# Ajoutez ici les autres tests pour EpicCustomer
