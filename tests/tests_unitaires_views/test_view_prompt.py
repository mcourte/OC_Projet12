import pytest
from unittest.mock import patch
import os
import sys

# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from views.prompt_view import PromptView  # Remplacez `your_module` par le nom de votre module


# Test de `prompt_confirm_statut`
def test_prompt_confirm_statut():
    with patch('questionary.confirm') as mock_confirm:
        mock_confirm.return_value.ask.return_value = True
        result = PromptView.prompt_confirm_statut()
        assert result is True


# Test de `prompt_select`
def test_prompt_select():
    with patch('questionary.select') as mock_select:
        mock_select.return_value.ask.return_value = 'Option1'
        result = PromptView.prompt_select('Select an option', ['Option1', 'Option2'])
        assert result == 'Option1'
