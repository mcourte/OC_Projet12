import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
import os
import sys
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from models.entities import Base
from cli.contract_cli import add_contract, list_contracts
import tempfile
# Configuration de la base de données en mémoire
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def temp_file():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def mock_contract_base():
    with patch('controllers.contract_controller.ContractBase') as mock:
        mock_instance = mock.return_value
        yield mock_instance


def test_add_contract_with_temp_file(mock_contract_base, temp_file):
    runner = CliRunner()
    mock_contract_base.create_contract.return_value = type('Contract', (object,), {'description': 'Test_add'})

    result = runner.invoke(add_contract, [
        'Test_add', '1000', '500', 'C', '115', 'N'
    ])

    print(f"DEBUG OUTPUT: {result.output}")
    assert result.exit_code == 0
    assert 'Contrat Test_add ajouté' in result.output


def test_list_contracts(mock_contract_base):
    runner = CliRunner()
    mock_contract_base.get_all_contracts.return_value = [
        MagicMock(description="Test_add", total_amount="1000", remaining_amount="1000",
                  customer_id="115", state="C", paiement_state="N")
    ]
    result = runner.invoke(list_contracts)
    print(f"DEBUG OUTPUT: {result.output}")
    assert result.exit_code == 0
    assert 'Test_add Créé (115)' in result.output
