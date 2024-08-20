import pytest
from click.testing import CliRunner
import os
import sys
from unittest.mock import patch, MagicMock
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)


from cli.event_cli import add_event, list_events


@pytest.fixture
def mock_event_base():
    with patch('controllers.event_controller.EventBase') as mock:
        mock_instance = mock.return_value
        mock_instance.login.return_value = True
        mock_instance.add_event.return_value = None
        mock_instance.list_events.return_value = None

        yield mock_instance


def test_add_event(mock_event_base):
    runner = CliRunner()
    mock_event_base.create_event.return_value = MagicMock(title='Test Event')
    result = runner.invoke(add_event, [
        "Test Event", "Test Description", "Test Location", "140", "2024-01-01", "2024-01-02"
    ])
    assert result.exit_code == 0
    assert 'Evènement Test Event ajouté avec succès' in result.output


def test_list_events(mock_event_base):
    runner = CliRunner()
    mock_event_base.get_all_events.return_value = [
        MagicMock(title='Test Event', location='Test Location', attendees='140')
    ]
    result = runner.invoke(list_events)
    assert result.exit_code == 0
    assert 'Test Event Test Location (140)' in result.output
