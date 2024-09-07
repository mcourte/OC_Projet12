import unittest
from unittest.mock import MagicMock, patch, Mock
from controllers.decorator import is_commercial, is_support, is_authenticated, is_admin, requires_roles
from models.entities import EpicUser
from config_test import SECRET_KEY, ALGORITHM


class TestDecorators(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock()  # Simule une session de base de données
        self.user = EpicUser(username="mcourte", state='A', role="ADM")  # Utilisateur simulé

    @patch('controllers.session.load_session')
    @patch('controllers.session.decode_token')
    def test_is_commercial(self, mock_decode_token, mock_load_session):
        mock_load_session.return_value = 'mocked_token'
        mock_decode_token.return_value = {'role': 'COM'}

        @is_commercial
        def test_func():
            return "Accès commercial autorisé"

        result = test_func()
        self.assertEqual(result, "Accès commercial autorisé")
        mock_load_session.assert_called_once()
        mock_decode_token.assert_called_once_with('mocked_token', SECRET_KEY, ALGORITHM)

    @patch('controllers.session.load_session')
    @patch('controllers.session.decode_token')
    def test_is_commercial_raises_permission_error(self, mock_decode_token, mock_load_session):
        mock_load_session.return_value = 'mocked_token'
        mock_decode_token.return_value = {'role': 'SUP'}  # Rôle incorrect pour ce test

        @is_commercial
        def test_func():
            return "Accès commercial autorisé"

        with self.assertRaises(PermissionError):
            test_func()

    @patch('controllers.session.load_session')
    @patch('controllers.session.decode_token')
    def test_is_authenticated(self, mock_decode_token, mock_load_session):
        mock_load_session.return_value = 'mocked_token'
        mock_decode_token.return_value = {'username': 'mcourte'}
        self.session.query.return_value.filter_by.return_value.one_or_none.return_value = self.user

        @is_authenticated
        def test_func(cls, session):
            return "Utilisateur authentifié"

        result = test_func(self, self.session)
        self.assertEqual(result, "Utilisateur authentifié")
        mock_load_session.assert_called_once()
        mock_decode_token.assert_called_once_with('mocked_token', SECRET_KEY, ALGORITHM)
        self.session.query.assert_called_once()

    @patch('controllers.session.load_session')
    @patch('controllers.session.decode_token')
    def test_is_authenticated_inactive_user(self, mock_decode_token, mock_load_session):
        mock_load_session.return_value = 'mocked_token'
        mock_decode_token.return_value = {'username': 'pcourant'}
        self.session.query.return_value.filter_by.return_value.one_or_none.return_value = None

        @is_authenticated
        def test_func(cls, session):
            return "Utilisateur authentifié"

        with self.assertRaises(PermissionError):
            test_func(self, self.session)

    @patch('controllers.session.load_session')
    @patch('controllers.session.decode_token')
    def test_is_admin_valid_role(self, mock_decode_token, mock_load_session):
        """
        Test du décorateur `is_admin` avec un rôle valide.
        """
        mock_decode_token.return_value = {'role': 'ADM'}

        @is_admin
        def dummy_function(cls, session):
            return "Success"

        self.assertEqual(dummy_function(Mock(), Mock()), "Success")

    @patch('controllers.session.load_session')
    @patch('controllers.session.decode_token')
    def test_is_admin_invalid_role(self, mock_decode_token, mock_load_session):
        """
        Test du décorateur `is_admin` avec un rôle invalide.
        """
        mock_decode_token.return_value = {'role': 'COM'}

        @is_admin
        def dummy_function(cls, session):
            return "Success"

        with self.assertRaises(ValueError):
            dummy_function(Mock(), Mock())

    @patch('controllers.session.load_session')
    @patch('controllers.session.decode_token')
    def test_requires_roles_valid_role(self, mock_decode_token, mock_load_session):
        """
        Test du décorateur `requires_roles` avec un rôle valide.
        """
        mock_decode_token.return_value = {'role': 'COM'}

        @requires_roles('COM', 'ADM')
        def dummy_function(cls, session):
            return "Success"

        self.assertEqual(dummy_function(Mock(), Mock()), "Success")

    @patch('controllers.session.load_session')
    @patch('controllers.session.decode_token')
    def test_requires_roles_invalid_role(self, mock_decode_token, mock_load_session):
        mock_load_session.return_value = 'mocked_token'
        mock_decode_token.return_value = {'role': 'SUP'}

        @requires_roles('COM', 'ADM')
        def dummy_function(cls, session):
            return "Success"

        with self.assertRaises(PermissionError):
            dummy_function(self, self.session)

    @patch('controllers.session.load_session')
    def test_requires_roles_token_not_found(self, mock_load_session):
        mock_load_session.side_effect = Exception("Token not found")

        @requires_roles('COM', 'ADM')
        def dummy_function(cls, session):
            return "Success"

        with self.assertRaises(PermissionError):
            dummy_function(self, self.session)


if __name__ == '__main__':
    unittest.main()
