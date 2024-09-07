import sys
import os
import unittest
from unittest.mock import patch, MagicMock, call
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

    @patch('rich.console.Console.print')
    def test_display_profil(self, mock_print):
        # Création d'un mock pour l'utilisateur
        mock_user = MagicMock()
        mock_user.first_name = 'John'
        mock_user.last_name = 'Doe'
        mock_user.email = 'john.doe@example.com'
        mock_user.role.value = 'Admin'
        mock_user.state.value = 'Active'

        # Appel à la méthode display_profil
        DataView.display_profil(mock_user)

        # Définir le texte attendu à afficher dans le Panel
        expected_text = (
            "Prénom: John\n"
            "Nom: Doe\n"
            "Email: john.doe@example.com\n"
            "Rôle: Admin\n"
            "État: Active\n"
        )

        # Définir le Panel attendu
        expected_panel = Panel(
            Align.center(expected_text, vertical='bottom'),
            box=box.ROUNDED,
            style='cyan',
            title_align='center',
            title='Mes informations'
        )

        # Vérification des attributs du Panel
        mock_print.assert_called_once()
        actual_panel = mock_print.call_args[0][0]

        self.assertEqual(actual_panel.title, expected_panel.title)
        self.assertEqual(actual_panel.box, expected_panel.box)
        self.assertEqual(actual_panel.style, expected_panel.style)
