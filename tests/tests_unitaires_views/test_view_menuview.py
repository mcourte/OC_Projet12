
import pytest
import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from rich.panel import Panel
from rich.columns import Columns
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)


from views.menu_view import MenuView
from views.console_view import error_console


class TestMenuView(unittest.TestCase):

    @patch('time.sleep', return_value=None)  # Mock pour éviter une vraie pause
    def test_thinking(self, mock_sleep):
        MenuView.thinking()
        mock_sleep.assert_called_once_with(30)

    @patch('views.menu_view.console.status')  # Mock de `console.status`
    def test_show_waiting(self, mock_status):
        mock_function = MagicMock()
        mock_status.return_value.__enter__.return_value = None  # Mock du contexte
        MenuView.show_waiting(mock_function)
        mock_function.assert_called_once()
        mock_status.assert_called_once_with("Working...", spinner="circleQuarters")

    def test_menu_gestion(self):
        panel = MenuView.menu_gestion()
        self.assertIsInstance(panel, Panel)
        self.assertIn('Menu Gestion', panel.title)
        self.assertIn('07-Créer un nouvel employé', panel.renderable.plain)

    def test_menu_admin(self):
        panel = MenuView.menu_admin()
        self.assertIsInstance(panel, Panel)
        self.assertIn('Menu Admin', panel.title)
        self.assertIn('07-Changer le statut actif/inactif d\'un employé', panel.renderable.plain)

    def test_menu_commercial(self):
        panel = MenuView.menu_commercial()
        self.assertIsInstance(panel, Panel)
        self.assertIn('Menu Commercial', panel.title)
        self.assertIn('07-Créer un nouveau client', panel.renderable.plain)

    def test_menu_support(self):
        panel = MenuView.menu_support()
        self.assertIsInstance(panel, Panel)
        self.assertIn('Menu Support', panel.title)
        self.assertIn('07-Modifier un évènement', panel.renderable.plain)

    def test_menu_role(self):
        roles = {
            'GES': MenuView.menu_gestion(),
            'COM': MenuView.menu_commercial(),
            'SUP': MenuView.menu_support(),
            'ADM': MenuView.menu_admin()
        }

        for role, expected_menu in roles.items():
            panel = MenuView.menu_role(role)
            self.assertIsInstance(panel, Panel)
            self.assertEqual(panel.title, expected_menu.title)

        # Test un rôle non reconnu
        panel = MenuView.menu_role('UNKNOWN')
        self.assertIsInstance(panel, Panel)
        self.assertIn('Menu non trouvé', panel.renderable.plain)

    @patch('views.menu_view.questionary.text')
    @patch('views.menu_view.console.print')
    @patch('views.menu_view.console.print')
    @patch('views.menu_view.Columns')
    def test_menu_choice(self, mock_columns, mock_print, mock_text):
        mock_text.return_value.ask.return_value = '07'
        mock_columns.return_value = Columns([MenuView.menu_accueil(), MenuView.menu_gestion(), MenuView.menu_quit()])

        result = MenuView.menu_choice('GES')
        self.assertEqual(result, '07')
        mock_text.assert_called_once()
        mock_print.assert_called()  # Vérifie que la méthode print a été appelée

    @patch('views.menu_view.questionary.text')
    @patch('views.menu_view.console.print')
    @patch('views.menu_view.console.print')
    @patch('views.menu_view.Columns')
    def test_menu_choice_invalid_input(self, mock_columns, mock_print, mock_text):
        mock_text.side_effect = ['99', '07']  # Première valeur invalide, deuxième valeur valide
        mock_columns.return_value = Columns([MenuView.menu_accueil(), MenuView.menu_gestion(), MenuView.menu_quit()])

        result = MenuView.menu_choice('GES')
        self.assertEqual(result, '07')
        mock_text.assert_called()
        error_console.print.assert_called_once_with('Votre choix est invalide')
