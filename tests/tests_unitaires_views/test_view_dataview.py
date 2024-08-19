import io
import sys
import pytest
import os
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)


from views.data_view import DataView


# Test de `display_workflow`
def test_display_workflow():
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()
    DataView.display_workflow()
    output = sys.stdout.getvalue().strip()
    sys.stdout = original_stdout
    assert output == 'Mise à jour du workflow'


# Test de `display_nocontracts`
def test_display_nocontracts():
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()
    DataView.display_nocontracts()
    output = sys.stdout.getvalue().strip()
    sys.stdout = original_stdout
    assert output == 'Aucun contrat trouvé'


# Test de `display_interupt`
def test_display_interupt():
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()
    DataView.display_interupt()
    output = sys.stdout.getvalue().strip()
    sys.stdout = original_stdout
    assert output == 'Opération abandonée'


# Test de `display_error_contract_amount`
def test_display_error_contract_amount():
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()
    DataView.display_error_contract_amount()
    output = sys.stdout.getvalue().strip()
    sys.stdout = original_stdout
    assert output == 'Ce montant est supérieur au restant dû'


# Test de `display_commercial_with_contracts`
def test_display_commercial_with_contracts():
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()
    DataView.display_commercial_with_contracts()
    output = sys.stdout.getvalue().strip()
    sys.stdout = original_stdout
    assert output == 'Ce commercial gère des contracts actifs'


# Test de `display_need_one_manager`
def test_display_need_one_manager():
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()
    DataView.display_need_one_manager()
    output = sys.stdout.getvalue().strip()
    sys.stdout = original_stdout
    assert output == 'La base doit contenir au moins un manager'


# Test de `display_error_unique`
def test_display_error_unique():
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()
    DataView.display_error_unique()
    output = sys.stdout.getvalue().strip()
    sys.stdout = original_stdout
    assert output == 'Impossible: cet enregistrement existe déjà'


# Test de `display_error_contract_need_c`
def test_display_error_contract_need_c():
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()
    DataView.display_error_contract_need_c()
    output = sys.stdout.getvalue().strip()
    sys.stdout = original_stdout
    assert output == "Le contract doit être à l'état créé"


# Test de `display_data_update`
def test_display_data_update():
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()
    DataView.display_data_update()
    output = sys.stdout.getvalue().strip()
    sys.stdout = original_stdout
    assert output == 'Vos modifications ont été enregistrées'
