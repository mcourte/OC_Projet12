import pytest
from click.testing import CliRunner
import os
import sys
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from cli.contract_cli import add_contract, list_contracts
from models.entities import Base

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
def mock_contract_base():
    with patch('controllers.contract_controller.ContractBase') as mock:
        mock_instance = mock.return_value
        mock_instance.create_contract.return_value = MagicMock(contract_id=123)
        mock_instance.get_all_contracts.return_value = [
            MagicMock(title='Test Contract', location='Test Location', attendees='Test Attendees')
        ]
        yield mock_instance


@pytest.fixture
def temp_file():
    import tempfile
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_add_contract_with_temp_file(mock_contract_base, temp_file):
    runner = CliRunner()
    with open(temp_file, 'w') as f:
        f.write('temporary contract data')

    result = runner.invoke(add_contract, [
        'Contract Description', '1000', '500', 'Active', 'C001', 'Paid', '--config', temp_file
    ])
    print(f"DEBUG OUTPUT: {result.output}")  # Pour déboguer la sortie
    assert result.exit_code == 0
    assert 'Contract 123 added successfully' in result.output

    with open(temp_file, 'r') as f:
        content = f.read()
        assert 'temporary contract data' in content


def test_add_contract_failure_with_temp_file(mock_contract_base, temp_file):
    runner = CliRunner()
    with open(temp_file, 'w') as f:
        f.write('failure contract config')

    mock_contract_base.create_contract.side_effect
