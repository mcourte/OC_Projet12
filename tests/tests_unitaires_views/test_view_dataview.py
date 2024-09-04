import sys
import pytest
import os
import unittest
from unittest.mock import patch, MagicMock
from rich.panel import Panel
from rich.console import Console, Align
from rich import box
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from views.data_view import DataView


class TestDataView(unittest.TestCase):

    @patch.object(Console, 'print')
    def test_display_workflow(self, mock_print):
        DataView.display_workflow()
        mock_print.assert_called_once_with('Mise à jour du workflow')

    @patch.object(Console, 'print')
    def test_display_nocontracts(self, mock_print):
        DataView.display_nocontracts()
        mock_print.assert_called_once_with('Aucun contrat trouvé')

    @patch.object(Console, 'print')
    def test_display_interupt(self, mock_print):
        DataView.display_interupt()
        mock_print.assert_called_once_with('Opération abandonnée')

    @patch.object(Console, 'print')
    def test_display_data_update(self, mock_print):
        DataView.display_data_update()
        mock_print.assert_called_once_with('Vos modifications ont été enregistrées')

    @patch.object(Console, 'print')
    @patch('views.console_view.Panel', autospec=True)
    def test_display_profil(self, mock_panel, mock_print):
        # Création d'un mock pour l'utilisateur
        mock_user = MagicMock()
        mock_user.first_name = 'John'
        mock_user.last_name = 'Doe'
        mock_user.email = 'john.doe@example.com'
        mock_user.role.value = 'Admin'
        mock_user.state.value = 'Active'

        # Configure le mock Panel pour vérifier les appels
        mock_panel.return_value = Panel(
            Align.center('Prénom: John\nNom: Doe\nEmail: john.doe@example.com\nRôle: Admin\nÉtat: Active\n', vertical='bottom'),
            box=box.ROUNDED,
            style='cyan',
            title_align='center',
            title='Mes informations'
        )

        DataView.display_profil(mock_user)

        # Vérifier que Panel a été appelé avec les bons arguments
        mock_panel.assert_called_once_with(
            Align.center('Prénom: John\nNom: Doe\nEmail: john.doe@example.com\nRôle: Admin\nÉtat: Active\n', vertical='bottom'),
            box=box.ROUNDED,
            style='cyan',
            title_align='center',
            title='Mes informations'
        )
        mock_print.assert_called_once_with(mock_panel.return_value)
