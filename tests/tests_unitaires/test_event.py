import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.entities import Base
from controllers.event_controller import EventBase
from datetime import datetime


@pytest.fixture(scope='module')
def session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


def test_create_event(session):
    event_controller = EventBase(session)
    create_data = {
        'title': 'Company Meeting',
        'date_started': datetime(2023, 1, 1, 10, 0, 0),
        'date_ended': datetime(2023, 1, 1, 12, 0, 0),
        'description': 'Annual meeting',
        'location': 'Conference Room',
        'attendees': 10,
        'report': 'Summary Report',
        'customer_id': None,
        'support_id': None,
        'contract_id': None
    }
    event = event_controller.create_event(create_data)
    assert event.title == 'Company Meeting'


def test_get_event(session):
    event_controller = EventBase(session)
    event = event_controller.get_event(1)

    assert event is not None
    assert event.title == 'Company Meeting'


def test_update_event(session):
    event_controller = EventBase(session)
    update_data = {
        'title': 'Updated Meeting',
        'date_started': datetime(2023, 1, 1, 10, 0, 0),
        'date_ended': datetime(2023, 1, 1, 12, 0, 0),
    }
    event_controller.update_event(1, update_data)
    updated_event = event_controller.get_event(1)
    assert updated_event.title == 'Updated Meeting'


def test_delete_event(session):
    event_controller = EventBase(session)
    event_controller.delete_event(1)
    event = event_controller.get_event(1)

    assert event is None
