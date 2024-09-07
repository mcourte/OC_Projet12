import os
import sys
import unittest
from unittest.mock import patch, MagicMock
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)


from views.contract_view import ContractView
from rich.console import Console


class TestContractView(unittest.TestCase):

    @patch.object(Console, 'print')
    def test_display_list_contracts(self, mock_print):
        # Mock data
        mock_contract = MagicMock()
        mock_contract.description = "Contract A"
        mock_contract.customer.first_name = "John"
        mock_contract.customer.last_name = "Doe"
        mock_contract.remaining_amount = 100
        mock_contract.total_amount = 1000
        mock_contract.state.value = "Active"
        mock_contract.customer.commercial.username = "jdoe"
        mock_contract.gestion_id = "123"
        mock_contract.events = []

        ContractView.display_list_contracts([mock_contract])
        # Check if print was called
        mock_print.assert_called()
        # Additional assertions can be made based on how your data is formatted

    @patch.object(Console, 'print')
    def test_display_contract_info(self, mock_print):
        # Mock data
        mock_contract = MagicMock()
        mock_contract.contract_id = 1
        mock_contract.description = "Contract A"
        mock_contract.customer.first_name = "John"
        mock_contract.customer.last_name = "Doe"
        mock_contract.total_amount = 1000
        mock_contract.remaining_amount = 100
        mock_contract.state.value = "Active"
        mock_contract.events = []
        mock_contract.customer.commercial.username = "jdoe"

        ContractView.display_contract_info(mock_contract)
        mock_print.assert_called()
        # Additional assertions can be made based on how your data is formatted

    @patch("questionary.text")
    def test_prompt_data_contract(self, mock_text):
        # Configurez les entrées simulées pour questionary.text
        def mock_ask(text):
            responses = {
                "Référence:": "REF123",
                "Description:": "Contract Description",
                "Montant:": "500"
            }
            return responses.get(text, "")

        mock_text.return_value = MagicMock(ask=lambda: mock_ask(mock_text.call_args[0][0]))

        # Mettez en place la configuration nécessaire pour regexformat
        with patch('views.regexformat', {
            '3cn': [r'^[a-zA-Z]+$', "Invalid reference"],
            'all_letters': [r'^[a-zA-Z\s]+$', "Invalid description"],
            'numposmax': [r'^\d+$', "Invalid amount"]
        }):
            data = ContractView.prompt_data_contract()

        self.assertEqual(data, {
            'ref': 'REF123',
            'description': 'Contract Description',
            'total_amount': '500'
        })
        # Vérifiez que questionary.text a été appelé le bon nombre de fois
        self.assertEqual(mock_text.call_count, 3)

    @patch("questionary.text")
    def test_prompt_data_paiement(self, mock_text):
        # Configurez les entrées simulées pour questionary.text
        def mock_ask(text):
            responses = {
                "Référence:": "PAY123",
                "Montant:": "250"
            }
            return responses.get(text, "")

        mock_text.return_value = MagicMock(ask=lambda: mock_ask(mock_text.call_args[0][0]))

        data = ContractView.prompt_data_paiement()

        self.assertEqual(data, {
            'paiement_id': 'PAY123',
            'amount': '250'
        })
        # Vérifiez que questionary.text a été appelé le bon nombre de fois
        self.assertEqual(mock_text.call_count, 2)

    @patch("questionary.confirm")
    def test_prompt_confirm_contract_state(self, mock_confirm):
        mock_confirm.return_value.ask.return_value = True

        result = ContractView.prompt_confirm_contract_state()

        self.assertTrue(result)
        mock_confirm.assert_called_once_with("Souhaitez-vous trier les contrats par statut ?")

    @patch("questionary.confirm")
    def test_prompt_add_gestion(self, mock_confirm):
        mock_confirm.return_value.ask.return_value = True

        result = ContractView.prompt_add_gestion()

        self.assertTrue(result)
        mock_confirm.assert_called_once_with("Souhaitez-vous ajouter un gestionnaire à ce contrat ?")

    @patch("questionary.confirm")
    def test_prompt_confirm_contract_paiement(self, mock_confirm):
        mock_confirm.return_value.ask.return_value = True

        result = ContractView.prompt_confirm_contract_paiement()

        self.assertTrue(result)
        mock_confirm.assert_called_once_with("Souhaitez-vous trier les contrats par solde ?")

    @patch("questionary.select")
    def test_prompt_choose_paiement_state(self, mock_select):
        mock_select.return_value.ask.return_value = "Contrats soldés"

        result = ContractView.prompt_choose_paiement_state()

        self.assertEqual(result, "Contrats soldés")
        mock_select.assert_called_once_with(
            "Sélectionnez l'état de paiement:",
            choices=["Contrats soldés", "Contrats non soldés"]
        )

    @patch("questionary.confirm")
    def test_prompt_confirm_filtered_contract(self, mock_confirm):
        mock_confirm.return_value.ask.return_value = True

        result = ContractView.prompt_confirm_filtered_contract()

        self.assertTrue(result)
        mock_confirm.assert_called_once_with("Souhaitez-vous voir uniquement les contrats qui vous sont affectés ?")

    @patch("questionary.select")
    def test_prompt_choose_state(self, mock_select):
        mock_select.return_value.ask.return_value = "Contrats signés"

        result = ContractView.prompt_choose_state()

        self.assertEqual(result, "Contrats signés")
        mock_select.assert_called_once_with(
            "Sélectionnez le type de contrat :",
            choices=["Contrats signés", "Contrats non signés"]
        )

    @patch("questionary.confirm")
    def test_prompt_confirm_customer(self, mock_confirm):
        mock_confirm.return_value.ask.return_value = True

        result = ContractView.prompt_confirm_customer()

        self.assertTrue(result)
        mock_confirm.assert_called_once_with("Souhaitez-vous choisir un client ?")

    @patch("questionary.select")
    def test_menu_update_contract(self, mock_select):
        mock_select.return_value.ask.return_value = "Modifier les données du contrat"

        result = ContractView.menu_update_contract("Active")

        self.assertEqual(result, 1)
        mock_select.assert_called_once_with(
            "Que voulez-vous faire ?",
            choices=['Modifier les données du contrat', 'Signer le contrat']
        )
