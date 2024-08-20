import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))
sys.path.insert(0, parent_dir)

from cli.customer_cli import add_customer, list_customers
from models.entities import Base  # Assurez-vous que le modèle Customer est importé ici

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
        mock_instance.create_customer.return_value = type('Customer', (object,), {'customer_id': '123'})
        mock_instance.get_all_customers.return_value = [
            type('Customer', (object,), {'first_name': 'John', 'last_name': 'Doe'})
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


def test_add_customer_with_temp_file(mock_customer_base, temp_file):
    runner = CliRunner()
    mock_customer_base.create_customer.return_value = MagicMock(customer_id='115')
    result = runner.invoke(add_customer, [
        'Vincent', 'Legendre', 'vlegendre@gmail.com', '110011001100', '110011001100' , '104'
    ])
    print(f"DEBUG OUTPUT: {result.output}")
    assert result.exit_code == 0
    assert 'ajouté avec succès' in result.output


def test_list_customers_with_temp_file(mock_customer_base, temp_file):
    runner = CliRunner()
    result = runner.invoke(list_customers)
    print(f"DEBUG OUTPUT: {result.output}")
    assert result.exit_code == 0
    assert 'Vincent Legendre' in result.output
