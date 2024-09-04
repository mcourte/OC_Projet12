import pytest
from unittest.mock import patch
import os
import sys
import unittest


# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from views.prompt_view import PromptView


class TestPromptView(unittest.TestCase):

    @patch('views.prompt_view.questionary.select')
    def test_prompt_select_success(self, mock_select):
        # Configuration du mock pour simuler une sélection réussie
        mock_select.return_value.ask.return_value = 'Option 1'

        # Appel de la méthode avec des paramètres de test
        result = PromptView.prompt_select('Choisissez une option:', ['Option 1', 'Option 2'])

        # Vérifications
        mock_select.assert_called_once_with(
            'Choisissez une option:', choices=['Option 1', 'Option 2']
        )
        self.assertEqual(result, 'Option 1')

    @patch('views.prompt_view.questionary.select')
    def test_prompt_select_interrupt(self, mock_select):
        # Configuration du mock pour simuler une interruption par l'utilisateur
        mock_select.return_value.ask.return_value = None

        # Test pour vérifier que KeyboardInterrupt est levé
        with self.assertRaises(KeyboardInterrupt):
            PromptView.prompt_select('Choisissez une option:', ['Option 1', 'Option 2'])

    @patch('views.prompt_view.questionary.select')
    def test_prompt_select_with_kwargs(self, mock_select):
        # Configuration du mock pour simuler une sélection réussie avec des kwargs
        mock_select.return_value.ask.return_value = 'Option 2'

        # Appel de la méthode avec des paramètres de test et des kwargs
        result = PromptView.prompt_select(
            'Choisissez une option:',
            ['Option 1', 'Option 2'],
            style='bold blue'
        )

        # Vérifications
        mock_select.assert_called_once_with(
            'Choisissez une option:', choices=['Option 1', 'Option 2'], style='bold blue'
        )
        self.assertEqual(result, 'Option 2')
