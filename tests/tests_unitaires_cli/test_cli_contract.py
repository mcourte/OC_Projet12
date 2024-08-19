import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from models.entities import Base
from cli.contract_cli import add_contract, list_contracts

# Configuration de la base de données en mémoire
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="module")
def db_engine():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
    Base.metadata.create_all(bind=engine)  # Crée toutes les tables
    yield engine
    Base.metadata.drop_all(bind=engine)  # Nettoie après les tests


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
def temp_file():
    import tempfile
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def mock_contract_base():
    with patch('controllers.contract_controller.ContractBase') as mock:
        mock_instance = mock.return_value
        mock_instance.create_contract.return_value = MagicMock(contract_id='123')
        mock_instance.get_all_contracts.return_value = [
            MagicMock(title='Test Contract', location='Test Location', attendees='Test Attendees')
        ]
        yield mock_instance


def test_add_contract_with_temp_file(mock_contract_base, temp_file):
    runner = CliRunner()
    mock_contract_base.create_contract.return_value = MagicMock(contract_id='123')
    result = runner.invoke(add_contract, [
        'Contract Description', '1000', '500', 'C', '1', 'N'
    ])
    assert result.exit_code == 0
    assert 'Contract ID 123 ajouté' in result.output


def test_list_contract_with_temp_file(mock_contract_base, temp_file):
    runner = CliRunner()
    mock_contract_base.get_all_contracts.return_value = [
        MagicMock(title='Test Contract', location='Test Location', attendees='Test Attendees')
    ]
    result = runner.invoke(list_contracts)
    assert result.exit_code == 0
    assert 'Test Contract Test Location (Test Attendees)' in result.output
