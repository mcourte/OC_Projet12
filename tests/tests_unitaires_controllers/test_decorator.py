import pytest
import unittest
from unittest.mock import patch, MagicMock, Mock
from models.entities import EpicUser
from controllers.decorator import is_commercial, is_support, is_authenticated, SECRET_KEY, ALGORITHM, is_admin
from controllers.decorator import requires_roles
from controllers.session import create_token


class TestDecorators(unittest.TestCase):

    def setUp(self):
        """
        Méthode exécutée avant chaque test.
        """
        self.session = MagicMock()  # Simule une session de base de données
        self.user = EpicUser(username="mcourte", state='A', role="ADM")  # Utilisateur simulé

    @patch('controllers.session.load_session')
    @patch('controllers.session.decode_token')
    def test_is_commercial(self, mock_decode_token, mock_load_session):
        """
        Test du décorateur `is_commercial` pour vérifier si un utilisateur a le rôle 'Commercial' ou 'COM'.
        """
        # Mock du jeton et du rôle décodé
        mock_load_session.return_value = 'mocked_token'
        mock_decode_token.return_value = {'role': 'COM'}

        # Fonction à décorer
        @is_commercial
        def test_func():
            return "Accès commercial autorisé"

        result = test_func()

        self.assertEqual(result, "Accès commercial autorisé")
        mock_load_session.assert_called_once()
        mock_decode_token.assert_called_once_with('mocked_token', SECRET_KEY, ALGORITHM)

    @patch('controllers.session.load_session')
    @patch('controllers.session.decode_token')
    def test_is_support(self, mock_decode_token, mock_load_session):
        """
        Test du décorateur `is_support` pour vérifier si un utilisateur a le rôle 'Support' ou 'SUP'.
        """
        # Mock du jeton et du rôle décodé
        mock_load_session.return_value = 'mocked_token'
        mock_decode_token.return_value = {'role': 'SUP'}

        # Fonction à décorer
        @is_support
        def test_func():
            return "Accès support autorisé"

        result = test_func()

        self.assertEqual(result, "Accès support autorisé")
        mock_load_session.assert_called_once()
        mock_decode_token.assert_called_once_with('mocked_token', SECRET_KEY, ALGORITHM)

    @patch('controllers.session.load_session')
    @patch('controllers.session.decode_token')
    def test_is_authenticated(self, mock_decode_token, mock_load_session):
        """
        Test du décorateur `is_authenticated` pour vérifier si un utilisateur est authentifié.
        """
        # Mock du jeton et du rôle décodé
        mock_load_session.return_value = 'mocked_token'
        mock_decode_token.return_value = {'username': 'mcourte'}

        # Simule la session de base de données
        self.session.query.return_value.filter_by.return_value.one_or_none.return_value = self.user

        # Fonction à décorer
        @is_authenticated
        def test_func(cls, session):
            return "Utilisateur authentifié"

        # Appel de la fonction décorée
        result = test_func(self, self.session)

        self.assertEqual(result, "Utilisateur authentifié")
        mock_load_session.assert_called_once()
        mock_decode_token.assert_called_once_with('mocked_token', SECRET_KEY, ALGORITHM)
        self.session.query.assert_called_once()

    @patch('controllers.session.load_session')
    @patch('controllers.session.decode_token')
    def test_is_commercial_raises_permission_error(self, mock_decode_token, mock_load_session):
        """
        Test du décorateur `is_commercial` qui doit lever une erreur de permission si le rôle n'est pas 'COM' ou 'Commercial'.
        """
        # Mock du jeton et du rôle décodé
        mock_load_session.return_value = 'mocked_token'
        mock_decode_token.return_value = {'role': 'SUP'}  # Rôle incorrect pour ce test

        # Fonction à décorer
        @is_commercial
        def test_func():
            return "Accès commercial autorisé"

        # Test si le décorateur lève une PermissionError
        with self.assertRaises(PermissionError):
            test_func()

        mock_load_session.assert_called_once()
        mock_decode_token.assert_called_once_with('mocked_token', SECRET_KEY, ALGORITHM)

    @patch('controllers.session.load_session')
    @patch('controllers.session.decode_token')
    def test_is_commercial_valid_role(self, mock_decode_token, mock_load_session):
        mock_decode_token.return_value = {'role': 'COM'}

        @is_commercial
        def dummy_function():
            return "Success"

        self.assertEqual(dummy_function(), "Success")

    @patch('controllers.session.load_session')
    @patch('controllers.session.decode_token')
    def test_is_commercial_invalid_role(self, mock_decode_token, mock_load_session):
        mock_decode_token.return_value = {'role': 'SUP'}

        @is_commercial
        def dummy_function():
            return "Success"

        with self.assertRaises(PermissionError):
            dummy_function()

    @patch('controllers.session.load_session')
    @patch('controllers.session.decode_token')
    def test_is_support_valid_role(self, mock_decode_token, mock_load_session):
        mock_decode_token.return_value = {'role': 'SUP'}

        @is_support
        def dummy_function():
            return "Success"

        self.assertEqual(dummy_function(), "Success")

    @patch('controllers.session.load_session')
    @patch('controllers.session.decode_token')
    def test_is_support_invalid_role(self, mock_decode_token, mock_load_session):
        mock_decode_token.return_value = {'role': 'COM'}

        @is_support
        def dummy_function():
            return "Success"

        with self.assertRaises(PermissionError):
            dummy_function()

    @patch('controllers.session.load_session')
    @patch('controllers.session.decode_token')
    @patch('models.entities.EpicUser')
    def test_is_authenticated_valid_user(self, mock_decode_token, mock_load_session, mock_user):
        mock_decode_token.return_value = {'username': 'mcourte'}
        mock_user.query.filter_by.return_value.one_or_none.return_value = self.user

        @is_authenticated
        def dummy_function(cls, session):
            return "Success"

        self.assertEqual(dummy_function(Mock(), self.session), "Success")

    @patch('controllers.session.load_session')
    @patch('controllers.session.decode_token')
    @patch('models.entities.EpicUser')
    def test_is_authenticated_inactive_user(self, mock_decode_token, mock_load_session, mock_user):
        mock_decode_token.return_value = {'username': 'pcourant'}
        mock_user.query.filter_by.return_value.one_or_none.return_value = None

        @is_authenticated
        def dummy_function(cls, session):
            return "Success"

        with self.assertRaises(PermissionError):
            dummy_function(Mock(), self.session)

    @patch('controllers.session.load_session')
    @patch('controllers.session.decode_token')
    def test_is_admin_valid_role(self, mock_decode_token, mock_load_session):
        mock_decode_token.return_value = {'role': 'Admin'}

        @is_admin
        def dummy_function(cls, session):
            return "Success"

        self.assertEqual(dummy_function(Mock(), Mock()), "Success")

    @patch('controllers.session.load_session')
    @patch('controllers.session.decode_token')
    def test_is_admin_invalid_role(self, mock_decode_token, mock_load_session):
        mock_decode_token.return_value = {'role': 'COM'}

        @is_admin
        def dummy_function(cls, session):
            return "Success"

        with self.assertRaises(PermissionError):
            dummy_function(Mock(), Mock())

    @patch('controllers.session.load_session')
    @patch('controllers.session.decode_token')
    def test_requires_roles_valid_role(self, mock_decode_token, mock_load_session):
        mock_decode_token.return_value = {'role': 'COM'}

        @requires_roles('COM', 'ADM')
        def dummy_function(cls, session):
            return "Success"

        self.assertEqual(dummy_function(Mock(), Mock()), "Success")

    @patch('controllers.session.load_session')
    @patch('controllers.session.decode_token')
    def test_requires_roles_invalid_role(self, mock_decode_token, mock_load_session):
        mock_load_session.return_value = 'mocked_token'
        mock_decode_token.return_value = {'role': 'SUP'}  # Rôle invalide pour ce test

        @requires_roles('COM', 'ADM')
        def dummy_function(cls, session):
            return "Success"

        with self.assertRaises(PermissionError):
            dummy_function(self, self.session)

    @patch('controllers.session.load_session')
    def test_requires_roles_token_not_found(self, mock_load_session):
        mock_load_session.side_effect = Exception("Token not found")  # Simule l'absence de jeton

        @requires_roles('COM', 'ADM')
        def dummy_function(cls, session):
            return "Success"

        with self.assertRaises(PermissionError, match="Token not found"):
            dummy_function(self, self.session)

    @patch('controllers.session.load_session')
    @patch('controllers.session.decode_token')
    def test_requires_roles_invalid_token(self, mock_decode_token, mock_load_session):
        mock_load_session.return_value = 'mocked_token'
        mock_decode_token.side_effect = Exception("Token invalid")  # Simule une erreur de jeton

        @requires_roles('COM', 'ADM')
        def dummy_function(cls, session):
            return "Success"

        with self.assertRaises(PermissionError, match="Token invalid"):
            dummy_function(self, self.session)

    @patch('controllers.session.load_session')
    @patch('controllers.session.decode_token')
    def test_requires_roles_no_role_in_token(self, mock_decode_token, mock_load_session):
        mock_load_session.return_value = 'mocked_token'
        mock_decode_token.return_value = {}  # Pas de rôle dans le token

        @requires_roles('COM', 'ADM')
        def dummy_function(cls, session):
            return "Success"

        with self.assertRaises(PermissionError, msg="User role is None, required one of ('COM', 'ADM')"):
            dummy_function(self, self.session)


if __name__ == "__main__":
    unittest.main()
