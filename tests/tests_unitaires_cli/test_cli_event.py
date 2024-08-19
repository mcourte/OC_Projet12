import pytest
from click.testing import CliRunner
import os
import sys
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from controllers.event_controller import EventBase
from cli.event_cli import add_event, list_events
from models.entities import Base

# Création d'une base de données en mémoire
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="module")
def db_engine():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=db_engine)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def mock_event_base():
    with patch('controllers.event_controller.EventBase') as mock:
        mock_instance = mock.return_value
        mock_instance.login.return_value = True
        mock_instance.add_event.return_value = None
        mock_instance.list_events.return_value = None
        yield mock_instance

@pytest.fixture
def temp_file():
    import tempfile
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)

def test_add_event_with_temp_file(mock_event_base, temp_file):
    runner = CliRunner()
    with open(temp_file, 'w') as f:
        f.write('temporary event data')

    mock_event_base.create_event.return_value = type('Event', (object,), {'title': 'Test Event'})
    result = runner.invoke(add_event, [
        'Test Event', 'Test Description', 'Test Location', 'Test Attendees', '2024-01-01', '2024-01-02', '--config', temp_file
    ])
    assert result.exit_code == 0
    assert 'Evènement Test Event ajouté avec succès' in result.output

    with open(temp_file, 'r') as f:
        content = f.read()
        assert 'temporary event data' in content

def test_add_event_failure_with_temp_file(mock_event_base, temp_file):
    runner = CliRunner()
    with open(temp_file, 'w') as f:
        f.write('failure event config')

    mock_event_base.return_value.create_event.side_effect = ValueError("Error")
    result = runner.invoke(add_event, [
        'Test Event', 'Test Description', 'Test Location', 'Test Attendees', '2024-01-01', '2024-01-02', '--config', temp_file
    ])
    assert result.exit_code == 0
    assert 'Error' in result.output

def test_list_events_with_temp_file(mock_event_base, temp_file):
    runner = CliRunner()
    mock_event_base.return_value.get_all_events.return_value = [
        type('Event', (object,), {'title': 'Test Event', 'location': 'Test Location', 'attendees': 'Test Attendees'})
    ]
    result = runner.invoke(list_events, ['--output', temp_file])
    assert result.exit_code == 0

    with open(temp_file, 'r') as f:
        output = f.read()
        assert 'Test Event Test Location (Test Attendees)' in output
