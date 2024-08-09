import pytest
from sqlalchemy import inspect
from models.entities import EpicUser, Customer, Event, Commercial, Support
from controllers.user_controller import EpicUserBase
from datetime import datetime


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


def test_database_structure(session):
    inspector = inspect(session.bind)
    tables = inspector.get_table_names()
    print("Tables dans la base de données :", tables)
    for table_name in tables:
        columns = inspector.get_columns(table_name)
        print(f"Colonnes dans {table_name} :", [column['name'] for column in columns])


def test_create_event(session):
    com_user = Commercial(first_name='John', last_name='Doe', username='jdoe', password='password',
                          email='jdoe@epic.com', role='COM')
    sup_user = Support(first_name='Romain', last_name='Martin', username='rmartin', password='password',
                       email='rmartin@epic.com', role='SUP')
    customer = Customer(first_name='Jane', last_name='Doe', email='jane.doe@example.com',
                        phone='1234567890', company_name='TestCorp', creation_time=datetime.utcnow(),
                        update_time=datetime.utcnow(), commercial=com_user)

    session.add(com_user)
    session.add(sup_user)
    session.add(customer)
    session.commit()

    event = Event(title='Test Event', date_started=datetime.utcnow(),
                  date_ended=datetime.utcnow(), customer=customer, support=sup_user)
    session.add(event)
    session.commit()

    events = session.query(Event).all()
    assert len(events) > 0
    assert events[0].title == 'Test Event'
