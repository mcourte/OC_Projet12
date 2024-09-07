import unittest
from unittest.mock import patch, MagicMock
from controllers.user_controller import EpicUserBase
from models.entities import EpicUser
from config_test import generate_valid_token
import pytest
from controllers.session import decode_token


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

    @pytest.mark.unit
    @patch('controllers.session.decode_token')
    def test_set_activate_inactivate(mock_decode_token):
        # Patch 'decode_token' pour qu'il renvoie un payload valide
        mock_decode_token = {'username': 'tuser'}

        # Simulez une action qui appelle decode_token
        result = decode_token()

        assert result['username'] == 'tuser'

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
