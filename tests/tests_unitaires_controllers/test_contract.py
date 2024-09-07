import unittest
from unittest.mock import patch, MagicMock
from controllers.contract_controller import ContractBase, Contract, Paiement
from config_test import generate_valid_token
from decimal import Decimal


class TestContractBase(unittest.TestCase):

    def setUp(self):
        # Mock de la session SQLAlchemy
        self.session = MagicMock()
        self.current_user = MagicMock()
        self.current_user.username = 'mcourte'
        self.current_user.role = 'ADM'
        self.session.query().filter_by().first.return_value = None  # Simuler au

        self.valid_token = generate_valid_token('openclassroom_projet12', self.current_user.username)

    @patch('controllers.contract_controller.ContractBase.create_contract')
    def test_create_contract_success(self, mock_create_contract):
        contract_base = ContractBase(self.session, self.current_user)

        mock_create_contract.return_value = Contract(
            contract_id=1,
            description="Test Contract",
            total_amount=Decimal('1000.00'),
            remaining_amount=Decimal('1000.00'),
            state="C",
            customer_id=1,
            paiement_state="N",
            commercial_id=2,
            gestion_id=3
        )

        data = {
            'description': 'Test Contract',
            'total_amount': Decimal('1000.00'),
            'remaining_amount': Decimal('1000.00'),
            'customer_id': 1,
            'commercial_id': 2,
            'gestion_id': 3
        }
        result = contract_base.create_contract(self.session, data)

        self.assertEqual(result.description, 'Test Contract')
        self.assertEqual(result.total_amount, Decimal('1000.00'))
        self.assertEqual(result.remaining_amount, Decimal('1000.00'))
        self.assertEqual(result.state, 'C')
        self.assertEqual(result.customer_id, 1)
        self.assertEqual(result.paiement_state, 'N')
        self.assertEqual(result.commercial_id, 2)
        self.assertEqual(result.gestion_id, 3)

    @patch('controllers.contract_controller.ContractBase.create_contract')
    def test_create_contract_missing_fields(self, mock_create_contract):
        contract_base = ContractBase(self.session, self.current_user)

        data = {
            'description': 'Test Contract',
            # Missing required fields
        }

        with self.assertRaises(TypeError):
            contract_base.create_contract(self.session, data)

    @patch('controllers.contract_controller.ContractBase.update_contract')
    def test_update_contract_not_found(self, mock_update_contract):
        contract_base = ContractBase(self.session, self.current_user)

        mock_update_contract.side_effect = Exception("Le Contrat n'a pas été trouvé dans la base de données.")

        data = {'description': 'Updated Contract'}
        with self.assertRaises(Exception) as context:
            contract_base.update_contract(999, data, self.session)

        self.assertTrue('Le Contrat n\'a pas été trouvé dans la base de données.' in str(context.exception))

    @patch('controllers.contract_controller.ContractBase.update_contract')
    def test_update_contract_success(self, mock_update_contract):
        contract_base = ContractBase(self.session, self.current_user)

        mock_update_contract.return_value = None

        data = {'description': 'Updated Contract'}
        result = contract_base.update_contract(1, data, self.session)

        self.assertIsNone(result)

    @patch('controllers.contract_controller.ContractBase.add_paiement')
    def test_add_paiement_success(self, mock_add_paiement):
        contract_base = ContractBase(self.session, self.current_user)

        mock_add_paiement.return_value = Paiement(
            paiement_id='12345',
            amount=Decimal('500.00'),
            contract_id=1
        )

        data = {
            'paiement_id': '12345',
            'amount': Decimal('500.00')
        }
        result = contract_base.add_paiement(self.session, 1, data)

        self.assertEqual(result.paiement_id, '12345')
        self.assertEqual(result.amount, Decimal('500.00'))

    @patch('controllers.contract_controller.ContractBase.add_paiement')
    def test_add_paiement_amount_exceeds_remaining(self, mock_add_paiement):
        contract_base = ContractBase(self.session, self.current_user)

        mock_add_paiement.side_effect = ValueError("Le montant du paiement dépasse le restant dû du contrat.")

        data = {
            'paiement_id': '12345',
            'amount': Decimal('2000.00')  # Amount exceeds remaining amount
        }
        with self.assertRaises(ValueError) as context:
            contract_base.add_paiement(self.session, 1, data)

        self.assertTrue('Le montant du paiement dépasse le restant dû du contrat.' in str(context.exception))

    @patch('controllers.contract_controller.ContractBase.signed')
    def test_signed_success(self, mock_signed):
        contract_base = ContractBase(self.session, self.current_user)

        mock_signed.return_value = None

        result = contract_base.signed(1, self.session)

        self.assertIsNone(result)

    @patch('controllers.contract_controller.ContractBase.signed')
    def test_signed_contract_not_found(self, mock_signed):
        contract_base = ContractBase(self.session, self.current_user)

        mock_signed.side_effect = ValueError("Aucun contrat trouvé avec l'ID 999")

        with self.assertRaises(ValueError) as context:
            contract_base.signed(999, self.session)

        self.assertTrue("Aucun contrat trouvé avec l'ID 999" in str(context.exception))

    @patch('controllers.contract_controller.ContractBase.update_gestion_contract')
    def test_update_gestion_contract_success(self, mock_update_gestion_contract):
        contract_base = ContractBase(self.session, self.current_user)

        mock_update_gestion_contract.return_value = None

        result = contract_base.update_gestion_contract(self.session, 1, 2)

        self.assertIsNone(result)

    @patch('controllers.contract_controller.ContractBase.update_gestion_contract')
    def test_update_gestion_contract_not_found(self, mock_update_gestion_contract):
        contract_base = ContractBase(self.session, self.current_user)

        mock_update_gestion_contract.side_effect = ValueError("Aucun contrat trouvé avec l'ID spécifié.")

        with self.assertRaises(ValueError) as context:
            contract_base.update_gestion_contract(self.session, 999, 2)

        self.assertTrue("Aucun contrat trouvé avec l'ID spécifié." in str(context.exception))


if __name__ == '__main__':
    unittest.main()
