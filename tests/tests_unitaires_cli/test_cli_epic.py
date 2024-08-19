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

from cli.epic_cli import login, logout, dashboard, initbase
from controllers.epic_controller import EpicBase
from controllers.epic_dashboard import EpicDashboard
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

@pytest.fixture
def temp_file():
    import tempfile
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)

def test_login_with_temp_file(mock_epic_base, temp_file):
    runner = CliRunner()
    with open(temp_file, 'w') as f:
        f.write('temporary login data')

    result = runner.invoke(login, ['--username', 'tuser', '--password', 'password', '--config', temp_file])
    assert result.exit_code == 0
    assert 'Connexion réussie' in result.output

    with open(temp_file, 'r') as f:
        content = f.read()
        assert 'temporary login data' in content

def test_logout_with_temp_file(mock_epic_base, temp_file):
    runner = CliRunner()
    result = runner.invoke(logout, ['--config', temp_file])
    assert result.exit_code == 0

def test_dashboard_with_temp_file(mock_epic_dashboard, temp_file):
    runner = CliRunner()
    result = runner.invoke(dashboard, ['--output', temp_file])
    assert result.exit_code == 0

    with open(temp_file, 'r') as f:
        content = f.read()
        assert 'Dashboard' in content  # Assuming the dashboard output contains the word 'Dashboard'

def test_initbase_with_temp_file(mock_epic_base, temp_file):
    runner = CliRunner()
    result = runner.invoke(initbase, ['--config', temp_file])
    assert result.exit_code == 0
