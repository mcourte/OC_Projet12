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

from cli.customer_cli import add_customer, list_customers
from models.entities import Base
from controllers.customer_controller import CustomerBase

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
def mock_customer_base():
    with patch('controllers.customer_controller.CustomerBase') as mock:
        mock_instance = mock.return_value
        mock_instance.login.return_value = True
        mock_instance.add_customer.return_value = None
        mock_instance.list_customers.return_value = None
        mock_instance.authenticate.return_value = True
        yield mock_instance


@pytest.fixture
def temp_file():
    import tempfile
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_add_customer_with_temp_file(mock_customer_base, temp_file):
    runner = CliRunner()
    with open(temp_file, 'w') as f:
        f.write('temporary customer data')

    mock_customer_base.create_customer.return_value = type('Customer', (object,), {'customer_id': 456})
    result = runner.invoke(add_customer, [
        'John', 'Doe', 'john@example.com', '1234567890', 'Company Inc.', 'C001', '--config', temp_file
    ])
    assert result.exit_code == 0
    assert 'Client 456 ajouté avec succès' in result.output

    with open(temp_file, 'r') as f:
        content = f.read()
        assert 'temporary customer data' in content


def test_add_customer_failure_with_temp_file(mock_customer_base, temp_file):
    runner = CliRunner()
    with open(temp_file, 'w') as f:
        f.write('failure customer config')

    mock_customer_base.return_value.create_customer.side_effect = ValueError("Error")
    result = runner.invoke(add_customer, [
        'John', 'Doe', 'john@example.com', '1234567890', 'Company Inc.', 'C001', '--config', temp_file
    ])
    assert result.exit_code == 0
    assert 'Error' in result.output


def test_list_customers_with_temp_file(mock_customer_base, temp_file):
    runner = CliRunner()
    mock_customer_base.get_all_customers.return_value = [
        type('Customer', (object,), {'first_name': 'John', 'last_name': 'Doe'})
    ]
    result = runner.invoke(list_customers, ['--output', temp_file])
    assert result.exit_code == 0

    with open(temp_file, 'r') as f:
        output = f.read()
        assert 'John Doe' in output
