import unittest
import pytest
from unittest.mock import patch, MagicMock
from controllers.user_controller import EpicUserBase
from models.entities import EpicUser
from config_test import generate_valid_token
from terminal.terminal_contract import EpicTerminalContract


class TestEpicBase(unittest.TestCase):

    def setUp(self):
        self.session = MagicMock()
        self.current_user = MagicMock(spec=EpicUser)
        self.current_user.username = 'mcourte'
        self.current_user.role = 'ADM'
        self.session.query().filter_by().first.return_value = self.current_user
        self.valid_token = generate_valid_token('openclassroom_projet12', self.current_user.username)

    # Supprimer l'utilisateur spécifique s'il existe
        user_to_delete = self.session.query(EpicUser).filter_by(username='jdoe').first()
        if user_to_delete:
            self.session.delete(user_to_delete)
            self.session.commit()

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

    def test_user_missing_required_field():
        with pytest.raises(ValueError):
            # Créer un utilisateur sans fournir un champ requis, par exemple 'email'
            EpicUserBase(password='password', first_name='Admin', last_name='User', role='Commercial')

    def test_valid_user_role():
        user = EpicUserBase(password='password', first_name='Admin', last_name='User', role='Admin')
        assert user.role == 'Admin'

    def test_invalid_user_role():
        with pytest.raises(ValueError):
            EpicUserBase(password='password', first_name='Admin', last_name='User', role='InvalidRole')

    def test_user_with_contracts(self):
        user = EpicUserBase(password='password', first_name='Admin', last_name='User', role='Admin')
        contract1 = EpicTerminalContract(user=user, contract_id=1)
        contract2 = EpicTerminalContract(user=user, contract_id=2)
        self.session.add(user)
        self.session.commit()

        assert len(user.contracts) == 2

    def test_user_edge_case():
        user = EpicUserBase(password='password', role='Commercial')  # Cas limite, nom vide
        with pytest.raises(ValueError):
            user.validate()  # Validation échoue pour nom vide


if __name__ == '__main__':
    unittest.main()
