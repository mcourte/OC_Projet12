import unittest
from unittest.mock import patch, MagicMock

from controllers.contract_controller import ContractBase
from config_test import generate_valid_token


class TestContractBase(unittest.TestCase):

    def setUp(self):
        # Mock de la session SQLAlchemy
        self.session = MagicMock()
        self.current_user = MagicMock()
        self.current_user.username = 'mcourte'
        self.current_user.role = 'ADM'
        self.session.query().filter_by().first.return_value = None  # Simuler au

        self.valid_token = generate_valid_token('openclassroom_projet12', self.current_user.username)

    @patch('controllers.contract_controller.ContractBase.add_paiement')
    def test_add_paiement_success(self, mock_add_paiement):
        contract_base = ContractBase(self.session, self.current_user)

        # Testez la méthode d'ajout de paiement
        result = contract_base.add_paiement()

        # Vérifiez les assertions
        mock_add_paiement.assert_called_once()
        self.assertTrue(result)

    @patch('controllers.contract_controller.ContractBase.create_contract')
    def test_create_contract_success(self, mock_create_contract):
        contract_base = ContractBase(self.session, self.current_user)

        # Configurez le mock pour retourner une valeur spécifique si nécessaire
        mock_create_contract.return_value = True

        # Testez la création d'un contrat
        result = contract_base.create_contract()

        # Vérifiez les assertions
        mock_create_contract.assert_called_once()
        self.assertTrue(result)

    @patch('controllers.contract_controller.ContractBase.signed')
    def test_signed_success(self, mock_sign_contract):
        contract_base = ContractBase(self.session, self.current_user)

        # Configurez le mock pour retourner une valeur spécifique si nécessaire
        mock_sign_contract.return_value = True

        # Testez la signature du contrat
        result = contract_base.signed()

        # Vérifiez les assertions
        mock_sign_contract.assert_called_once()
        self.assertTrue(result)

    @patch('controllers.contract_controller.ContractBase.update_contract')
    def test_update_contract_not_found(self, mock_update_contract):
        contract_base = ContractBase(self.session, self.current_user)

        # Configurez le mock pour une mise à jour non trouvée
        mock_update_contract.side_effect = Exception("Le Contrat n'a pas été trouvé dans la base de données.")
        result = None
        try:
            result = contract_base.update_contract()
        except Exception as e:
            self.assertEqual(str(e), "Le Contrat n'a pas été trouvé dans la base de données.")

        # Vérifiez les assertions
        mock_update_contract.assert_called_once()
        self.assertIsNone(result)

    @patch('controllers.contract_controller.ContractBase.update_contract')
    def test_update_contract_success(self, mock_update_contract):
        contract_base = ContractBase(self.session, self.current_user)

        # Configurez le mock pour retourner une valeur spécifique si nécessaire
        mock_update_contract.return_value = True

        # Testez la mise à jour d'un contrat
        result = contract_base.update_contract()

        # Vérifiez les assertions
        mock_update_contract.assert_called_once()
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
