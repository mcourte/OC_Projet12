import os
import sys
import unittest
from unittest.mock import patch, MagicMock
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)


from views.authentication_view import AuthenticationView


class TestAuthenticationView(unittest.TestCase):

    @patch('builtins.print')
    def test_display_logout(self, mock_print):
        AuthenticationView.display_logout()
        mock_print.assert_called_once_with("Vous êtes déconnecté")

    @patch('rich.console.Console.print')
    def test_display_welcome(self, mock_print):
        mock_console = MagicMock()
        AuthenticationView.console = mock_console
        username = "mcourte"
        AuthenticationView.display_welcome(username)
        mock_print.assert_called_once_with(f'Bienvenue {username} sur EpicEvent')

    @patch('builtins.print')
    @patch('views.console_view.console.status')
    def test_display_waiting_databasecreation(self, mock_status, mock_print):
        mock_function = MagicMock()
        mock_data = ("arg1", "arg2")
        AuthenticationView.display_waiting_databasecreation(mock_function, mock_data)
        mock_print.assert_called_once_with("Création de la base de données ...")
        mock_status.assert_called_once_with("Création de la base de données ...", spinner="circleQuarters")
        mock_function.assert_called_once_with(*mock_data)

    @patch('views.console_view.console.input')
    def test_display_login(self, mock_input):
        mock_input.side_effect = ["testuser", "testpassword"]
        result = AuthenticationView.display_login()
        self.assertEqual(result, ("testuser", "testpassword"))

    @patch('questionary.text')
    @patch('questionary.password')
    def test_prompt_login(self, mock_password, mock_text):
        mock_text.return_value.ask.return_value = "testuser"
        mock_password.return_value.ask.return_value = "testpassword"
        result = AuthenticationView.prompt_login()
        self.assertEqual(result, ("testuser", "testpassword"))

    @patch('views.console_view.console.print')
    def test_display_database_connection(self, mock_print):
        db_name = "test_db"
        AuthenticationView.display_database_connection(db_name)
        mock_print.assert_called_once_with(f'La base {db_name} est opérationnelle')

    @patch('questionary.text')
    @patch('questionary.password')
    def test_prompt_baseinit(self, mock_password, mock_text):
        mock_text.return_value.ask.return_value = "adminuser"
        mock_password.return_value.ask.return_value = "adminpassword"
        result = AuthenticationView.prompt_baseinit()
        self.assertEqual(result, ("adminuser", "adminpassword"))

    @patch('questionary.text')
    @patch('questionary.password')
    @patch('questionary.confirm')
    def test_prompt_manager(self, mock_confirm, mock_password, mock_text):
        mock_text.return_value.ask.return_value = "manageruser"
        mock_password.return_value.ask.side_effect = ["managerpassword", "managerpassword"]
        mock_confirm.return_value.ask.return_value = True
        result = AuthenticationView.prompt_manager()
        self.assertEqual(result, ("manageruser", "managerpassword"))

    @patch('questionary.confirm')
    def test_prompt_confirm_testdata(self, mock_confirm):
        mock_confirm.return_value.ask.return_value = True
        result = AuthenticationView.prompt_confirm_testdata()
        self.assertTrue(result)

        mock_confirm.return_value.ask.return_value = False
        result = AuthenticationView.prompt_confirm_testdata()
        self.assertFalse(result)
