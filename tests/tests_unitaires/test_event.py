import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import sys
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)
print(parent_dir)
from tests.conftest import Base
from controllers.event_controller import EventBase


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
