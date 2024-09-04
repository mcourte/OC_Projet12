import os
import sys
import unittest
from unittest.mock import patch
import re
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)


from views.authentication_view import AuthenticationView
from views.console_view import console


class TestAuthenticationView(unittest.TestCase):

    @patch.object(console, 'print')
    def test_display_logout(self, mock_print):
        AuthenticationView.display_logout()
        mock_print.assert_called_once_with("Vous êtes déconnecté")

    @patch.object(console, 'print')
    def test_display_welcome(self, mock_print):
        username = "testuser"
        AuthenticationView.display_welcome(username)
        expected_text = f"!!! Bienvenue {username} sur le CRM de EpicEvent !!!"
        mock_print.assert_called_once_with(expected_text, justify="center", style="bold blue")

    @patch("questionary.text")
    @patch("questionary.password")
    def test_prompt_login(self, mock_password, mock_text):
        mock_text.return_value.ask.return_value = 'testuser'
        mock_password.return_value.ask.return_value = 'password123'

        username, password = AuthenticationView.prompt_login()

        mock_text.assert_called_once_with("Identifiant:")
        mock_password.assert_called_once_with("Mot de passe:")
        self.assertEqual(username, 'testuser')
        self.assertEqual(password, 'password123')

    @patch.object(console, 'print')
    def test_display_database_connection(self, mock_print):
        db_name = "test_db"
        AuthenticationView.display_database_connection(db_name)
        expected_text = f'La base {db_name} est opérationnelle'
        mock_print.assert_called_once_with(expected_text, style="green")

    @patch("questionary.text")
    @patch("questionary.password")
    def test_prompt_baseinit(self, mock_password, mock_text):
        mock_text.return_value.ask.return_value = 'adminuser'
        mock_password.return_value.ask.return_value = 'adminpassword'

        username, password = AuthenticationView.prompt_baseinit()

        mock_text.assert_called_once_with(
            "Identifiant administrateur:",
            validate=lambda text: True
            if re.match(r"^[a-zA-Z]+$", text)
            else "Seuls des caractères alphabétiques sont autorisés"
        )
        mock_password.assert_called_once_with("Mot de passe administrateur:")
        self.assertEqual(username, 'adminuser')
        self.assertEqual(password, 'adminpassword')
