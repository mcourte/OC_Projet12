import pytest
import sys
import os
import jwt
from unittest.mock import patch, MagicMock
import unittest
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from controllers.epic_controller import EpicBase, EpicDatabase


class TestEpicBase(unittest.TestCase):

    @patch('views.console_view.console')
    @patch('controllers.epic_controllers.EpicDatabase')
    @patch('controllers.config.Config')
    def test_init(self, mock_config, mock_epic_database, mock_console):
        mock_session = MagicMock()
        mock_epic_database.return_value.session = mock_session
        mock_config.return_value.SECRET_KEY = "dummy_secret_key"

        epic_base = EpicBase()

        mock_console.print.assert_any_call("Initialisation de EpicBase...", style="bold green")
        self.assertIsInstance(epic_base.epic, EpicDatabase)
        self.assertEqual(epic_base.session, mock_session)
        mock_console.print.assert_called_with("Utilisateur actuel dans EpicBase : None", style="green")

    @patch('your_module.console')
    @patch('your_module.clear_session')
    @patch('your_module.AuthenticationView.prompt_login')
    @patch('your_module.create_session')
    @patch('your_module.create_token')
    @patch('your_module.EpicDatabase.check_connection')
    def test_login_success(self, mock_check_connection, mock_create_token, mock_create_session, mock_prompt_login, mock_clear_session, mock_console):
        mock_user = MagicMock()
        mock_user.to_dict.return_value = {"username": "test_user"}
        mock_check_connection.return_value = mock_user
        mock_prompt_login.return_value = ("test_user", "test_pass")
        mock_create_token.return_value = "test_token"

        epic_base = EpicBase()
        result = epic_base.login()

        mock_clear_session.assert_called_once()
        mock_prompt_login.assert_called_once()
        mock_create_session.assert_called_once_with({"username": "test_user"}, "test_token")
        mock_console.print.assert_called_with("Connexion réussie", style="bold blue")
        self.assertTrue(result)

    @patch('your_module.console')
    @patch('your_module.clear_session')
    @patch('your_module.AuthenticationView.prompt_login')
    @patch('your_module.EpicDatabase.check_connection')
    def test_login_failure(self, mock_check_connection, mock_prompt_login, mock_clear_session, mock_console):
        mock_check_connection.return_value = None
        mock_prompt_login.return_value = ("test_user", "test_pass")

        epic_base = EpicBase()
        result = epic_base.login()

        mock_clear_session.assert_called_once()
        mock_prompt_login.assert_called_once()
        mock_console.print.assert_called_with("Échec de la connexion", style="bold blue")
        self.assertFalse(result)

    @patch('views.console_view.console')
    @patch('controllers.session.load_session')
    @patch('controllers.session.jwt.decode')
    @patch('controllers.epic_controller.EpicDatabase.check_user')
    @patch('controllers.user_controller.EpicBase.authenticate_user')
    def test_check_session_valid(self, mock_authenticate_user, mock_check_user, mock_jwt_decode, mock_load_session, mock_console):
        mock_user = MagicMock()
        mock_check_user.return_value = mock_user
        mock_jwt_decode.return_value = {"username": "test_user"}
        mock_authenticate_user.return_value = True
        mock_load_session.return_value = "valid_token"

        epic_base = EpicBase()
        user = epic_base.check_session()

        mock_load_session.assert_called_once()
        mock_jwt_decode.assert_called_once_with("valid_token", epic_base.env.SECRET_KEY, algorithms=['HS256'])
        mock_check_user.assert_called_once_with("test_user")
        mock_authenticate_user.assert_called_once_with(epic_base.epic.session, "test_user", mock_user.password)
        self.assertEqual(user, mock_user)
        self.assertEqual(epic_base.current_user, mock_user)

    @patch('views.console_view.console')
    @patch('controllers.session.load_session')
    @patch('controllers.session.jwt.decode', side_effect=jwt.ExpiredSignatureError)
    def test_check_session_expired(self, mock_jwt_decode, mock_load_session, mock_console):
        mock_load_session.return_value = "expired_token"

        epic_base = EpicBase()
        user = epic_base.check_session()

        mock_load_session.assert_called_once()
        mock_jwt_decode.assert_called_once_with("expired_token", epic_base.env.SECRET_KEY, algorithms=['HS256'])
        mock_console.print.assert_called_with("Le jeton a expiré.", style="bold red")
        self.assertIsNone(user)

    @patch('views.console_view.console')
    @patch('controllers.session.load_session')
    @patch('controllers.session.jwt.decode', side_effect=jwt.InvalidTokenError)
    def test_check_session_invalid(self, mock_jwt_decode, mock_load_session, mock_console):
        mock_load_session.return_value = "invalid_token"

        epic_base = EpicBase()
        user = epic_base.check_session()

        mock_load_session.assert_called_once()
        mock_jwt_decode.assert_called_once_with("invalid_token", epic_base.env.SECRET_KEY, algorithms=['HS256'])
        mock_console.print.assert_called_with("Jeton invalide.", style="bold red")
        self.assertIsNone(user)

    @patch('views.console_view.console')
    @patch('controllers.session.save_session')
    @patch('controllers.session.create_token')
    def test_refresh_session(self, mock_create_token, mock_save_session, mock_console):
        epic_base = EpicBase()
        epic_base.current_user = MagicMock()

        mock_create_token.return_value = "new_token"

        epic_base.refresh_session()

        mock_create_token.assert_called_once_with(epic_base.current_user)
        mock_save_session.assert_called_once_with("new_token")

    @patch('views.console_view.console')
    @patch('controllers.session.save_session')
    def test_refresh_session_no_user(self, mock_save_session, mock_console):
        epic_base = EpicBase()
        epic_base.current_user = None

        epic_base.refresh_session()

        mock_save_session.assert_not_called()
        mock_console.print.assert_called_with("Aucun utilisateur connecté pour rafraîchir la session.", style="bold red")

    @patch('views.console_view.console')
    @patch('view.authentication_view.AuthenticationView.prompt_baseinit')
    @patch('controllers.config.Config.create_config')
    @patch('controllers.epic_controller.EpicDatabase')
    def test_initbase(self, mock_epic_database, mock_create_config, mock_prompt_baseinit, mock_console):
        mock_prompt_baseinit.return_value = ('db_name', 'username', 'password', 'port')

        EpicBase.initbase()

        mock_prompt_baseinit.assert_called_once()
        mock_create_config.assert_called_once_with('db_name', 'username', 'password', 'port')
        mock_epic_database.assert_called_once_with(database='db_name', host=mock.ANY, user='username', password='password', port='port')
        mock_console.print.assert_called_once_with("Base de données configurée avec succès.", style="bold green")

    @patch('views.console_view.console')
    @patch('models.entities.EpicUser')
    @patch('controllers.epic_controller.EpicDatabase')
    def test_authenticate_user_success(self, mock_epic_database, mock_epic_user, mock_console):
        session_mock = MagicMock()
        user_mock = MagicMock()
        user_mock.check_password.return_value = True
        session_mock.query().filter_by().first.return_value = user_mock

        epic_base = EpicBase()
        result = epic_base.authenticate_user(session_mock, 'username', 'password')

        session_mock.query().filter_by.assert_called_once_with(username='username')
        user_mock.check_password.assert_called_once_with('password')
        self.assertTrue(result)
        self.assertEqual(epic_base.current_user, user_mock)

    @patch('views.console_view.console')
    @patch('models.entities.EpicUser')
    @patch('controllers.epic_controller.EpicDatabase')
    def test_authenticate_user_failure(self, mock_epic_database, mock_epic_user, mock_console):
        session_mock = MagicMock()
        session_mock.query().filter_by().first.return_value = None

        epic_base = EpicBase()
        result = epic_base.authenticate_user(session_mock, 'username', 'password')

        session_mock.query().filter_by.assert_called_once_with(username='username')
        self.assertFalse(result)
        self.assertIsNone(epic_base.current_user)
