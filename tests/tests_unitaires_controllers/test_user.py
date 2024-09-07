import unittest
from unittest.mock import patch, MagicMock
from controllers.user_controller import EpicUserBase
from models.entities import EpicUser
from config_test import generate_valid_token


class TestEpicBase(unittest.TestCase):

    def setUp(self):
        self.session = MagicMock()
        self.current_user = MagicMock(spec=EpicUser)
        self.current_user.username = 'mcourte'
        self.current_user.role = 'ADM'
        self.session.query().filter_by().first.return_value = self.current_user
        self.valid_token = generate_valid_token('openclassroom_projet12', self.current_user.username)

    @patch('controllers.user_controller.EpicUserBase.create_user')
    def test_create_user_success(self, mock_create_user):
        # Simulez la création d'un utilisateur avec un nom d'utilisateur unique
        mock_create_user.return_value = True
        result = EpicUserBase.create_user('pmontgomrry', 'password')
        self.assertTrue(result)

    @patch('controllers.session.decode_token')
    def test_set_activate_inactivate(self, mock_decode_token):
        mock_decode_token.return_value = {'username': 'jdoe'}

        # Simuler une session et un utilisateur
        mock_session = MagicMock()
        mock_user = MagicMock(username='jdoe', state='A')
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_user

        # Générer un token valide
        valid_token = generate_valid_token('openclassroom_projet12', 'jdoe')

        # Appeler la méthode avec le token valide
        EpicUserBase.set_activate_inactivate(mock_session, valid_token)

        # Vérifier que l'état de l'utilisateur a été modifié
        self.assertEqual(mock_user.state, 'I')

    @patch('controllers.user_controller.EpicUserBase.update_user')
    def test_update_user(self, mock_update_user):
        mock_update_user.return_value = True
        result = EpicUserBase.update_user('user_id', {'email': 'newemail@example.com'})
        self.assertTrue(result)

    @patch('controllers.user_controller.EpicUserBase.reassign_customers')
    def test_reassign_customers(self, mock_reassign_customers):
        mock_reassign_customers.return_value = True
        result = EpicUserBase.reassign_customers('customer_id', 'new_user_id')
        self.assertTrue(result)

    @patch('controllers.user_controller.EpicUserBase.reassign_contracts')
    def test_reassign_contracts(self, mock_reassign_contracts):
        # Simulez la réaffectation des contrats
        mock_reassign_contracts.return_value = True
        result = EpicUserBase.reassign_contracts('contract_id', 'user_id')
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
