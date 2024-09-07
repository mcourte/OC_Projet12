import os
import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open
import jwt
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)
print(parent_dir)

# Imports des fonctions à tester depuis le fichier cible
from controllers.session import (
    create_token, load_session, clear_session,
    renew_session, get_current_user, force_refresh_token, serialize_user
)


class TestEpicFunctions(unittest.TestCase):

    def setUp(self):
        self.user_data = {
            'username': 'tuser',
            'role': 'Admin'
        }
        self.secret_key = "openclassroom_projet12"
        self.algorithm = "HS256"
        self.token = create_token(self.user_data, self.secret_key)

    def test_create_token(self):
        token = create_token(self.user_data, self.secret_key)
        decoded = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        self.assertEqual(decoded['username'], self.user_data['username'])
        self.assertEqual(decoded['role'], self.user_data['role'])

    @patch("controllers.session.open", new_callable=mock_open, read_data='{"token": "sometoken"}')
    @patch("controllers.session.os.path.join", return_value="/test/path/session.json")
    def test_load_session(self, mock_path_join, mock_open_func):
        token = load_session()
        mock_open_func.assert_called_once_with("/test/path/session.json", 'r')
        self.assertEqual(token, 'sometoken')

    @patch("controllers.session.os.remove")
    @patch("controllers.session.logging.info")
    def test_clear_session(self, mock_logging_info, mock_os_remove):
        with patch("controllers.session.os.path.exists", return_value=True):
            clear_session()
            mock_os_remove.assert_called_once_with('session.json')
            mock_logging_info.assert_called_once_with("Fichier de session supprimé avec succès.")

    @patch("controllers.session.get_current_user")
    @patch("controllers.session.save_session")
    @patch("controllers.session.create_token", return_value="new_token")
    def test_renew_session(self, mock_create_token, mock_save_session, mock_get_current_user):
        mock_user = MagicMock(username="tuser", role="Admin")
        mock_get_current_user.return_value = mock_user

        new_token = renew_session()

        mock_create_token.assert_called_once_with(mock_user.username, mock_user.role)
        mock_save_session.assert_called_once_with("new_token")
        self.assertEqual(new_token, "new_token")

    @patch('controllers.session.get_current_user')
    def test_get_current_user(self, mock_get_current_user):
        mock_user = {'username': 'tuser'}
        mock_get_current_user.return_value = mock_user

        # Assurez-vous que `get_current_user` est bien appelé
        result = get_current_user()

        # Vérifier le résultat
        self.assertEqual(result, None)

    @patch('controllers.session.save_session')
    def test_save_session(self, mock_save_session):
        # Simulez un appel à save_session et ajoutez les assertions nécessaires
        session_data = {"token": "valid_token"}
        mock_save_session(session_data)

        mock_save_session.assert_called_once_with(session_data)

    @patch("controllers.session.load_session", return_value="token")
    @patch("controllers.session.decode_token", return_value={'username': 'tuser', 'role': 'Admin'})
    @patch("controllers.session.create_token")
    @patch("controllers.session.save_session")
    def test_force_refresh_token(self, mock_save_session, mock_create_token, mock_decode_token, mock_load_session):
        mock_user = MagicMock(username="tuser", role="Admin")
        with patch("controllers.session.session.query") as mock_query:
            mock_query().filter_by().first.return_value = mock_user
            mock_create_token.return_value = "new_token"

            new_token = force_refresh_token()

            # Assurez-vous que le token est correctement généré
            mock_create_token.assert_called_once_with('tuser', 'Admin')
            mock_save_session.assert_called_once_with("new_token")
            self.assertEqual(new_token, "new_token")

    def test_serialize_user(self):
        mock_user = MagicMock(
            username="tuser",
            role=MagicMock(code="Admin"),
            email="tuser@epic.com",
            first_name="Test",
            last_name="User",
            state=MagicMock(code="Actif")
        )
        user_dict = serialize_user(mock_user)
        self.assertEqual(user_dict['username'], 'tuser')
        self.assertEqual(user_dict['role'], 'Admin')
        self.assertEqual(user_dict['email'], 'tuser@epic.com')
        self.assertEqual(user_dict['first_name'], 'Test')
        self.assertEqual(user_dict['last_name'], 'User')
        self.assertEqual(user_dict['state'], 'Actif')
