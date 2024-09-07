import unittest
from unittest.mock import patch, MagicMock
from controllers.user_controller import EpicUserBase
from controllers.session import decode_token, load_session, create_session
from config_init import SECRET_KEY, ALGORITHM


class TestEpicBase(unittest.TestCase):

    @patch('controllers.session.sessionmaker')
    def test_authenticate_user_success(self, mock_sessionmaker):
        # Configurez le mock de sessionmaker pour retourner une session valide
        mock_session = MagicMock()
        mock_sessionmaker.return_value = mock_session

        # Configuration du mock pour les appels de méthodes
        mock_user = MagicMock()
        mock_user.user = "auser"
        mock_session.query().filter().first.return_value = mock_user

        # Instanciez votre EpicUserBase avec la session mockée
        user_base = EpicUserBase(session=mock_session, user=mock_user)

        # Utilisez la méthode correcte pour obtenir les informations utilisateur
        user_info = user_base.get_user_info()

        # Ajoutez les assertions appropriées pour tester le succès
        self.assertEqual(user_info.user, "auser")

    def test_check_session_invalid(self):
        invalid_token = "invalidtoken"
        with self.assertRaises(PermissionError):
            decode_token(invalid_token, SECRET_KEY, ALGORITHM)

    def test_login_success(self):
        username = "testuser"
        role = "Admin"
        user_data = {'username': username, 'role': role}
        create_session(user_data, role)
        token = load_session()
        self.assertIsNotNone(token, "Token should be created and saved.")
        decoded = decode_token(token, SECRET_KEY, ALGORITHM)
        self.assertIsInstance(decoded, dict)
        self.assertEqual(decoded.get('username'), username, "Username should match.")
        self.assertEqual(decoded.get('role'), role, "Role should match.")


if __name__ == '__main__':
    unittest.main()
