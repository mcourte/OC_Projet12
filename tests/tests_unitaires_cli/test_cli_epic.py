import pytest
from click.testing import CliRunner
import os
import sys
from unittest.mock import patch
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from cli.epic_cli import login, logout, dashboard, initbase


@pytest.fixture
def mock_epic_base():
    with patch('controllers.epic_controller.EpicBase') as mock:
        mock_instance = mock.return_value
        mock_instance.login.return_value = True
        mock_instance.logout.return_value = None
        mock_instance.dashboard.return_value = None
        mock_instance.initdb.return_value = None
        yield mock_instance


@pytest.fixture
def mock_epic_dashboard():
    with patch('controllers.epic_dashboard.EpicDashboard') as mock:
        mock_instance = mock.return_value
        mock_instance.run.return_value = None
        yield mock_instance


def test_login_with_temp_file(mock_epic_base, temp_file):
    runner = CliRunner()
    with open(temp_file, 'w') as f:
        f.write('temporary login data')

    result = runner.invoke(login, ['--username', 'auser', '--password', 'password', '--config', temp_file])

    # Add debug prints
    print(f"CLI Output: {result.output}")
    print(f"Exit Code: {result.exit_code}")

    assert result.exit_code == 0
    assert 'Connexion réussie' in result.output


def test_logout_with_temp_file(mock_epic_base, temp_file):
    runner = CliRunner()
    result = runner.invoke(logout, ['--config', temp_file])
    assert result.exit_code == 0
    assert 'Déconnexion réussie' in result.output


def test_dashboard_with_temp_file(mock_epic_dashboard, temp_file):
    runner = CliRunner()
    result = runner.invoke(dashboard, ['--output', temp_file])
    assert result.exit_code == 0
    assert 'Dashboard Content' in result.output


def test_initbase_with_temp_file(mock_epic_base, temp_file):
    runner = CliRunner()
    result = runner.invoke(initbase, ['--config', temp_file])
    assert result.exit_code == 0
    assert 'Base de données initialisée' in result.output
