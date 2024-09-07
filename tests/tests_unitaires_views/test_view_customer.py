import unittest
from unittest.mock import patch, MagicMock
from views.customer_view import CustomerView
from datetime import datetime


class TestCustomerView(unittest.TestCase):

    @patch('views.prompt_view.PromptView.prompt_select')
    def test_prompt_client(self, mock_prompt_select):
        # Mock des données
        all_customers = ["John Doe", "Jane Smith"]
        mock_prompt_select.return_value = "John Doe"

        result = CustomerView.prompt_client(all_customers)

        self.assertEqual(result, "John Doe")
        mock_prompt_select.assert_called_once_with("Choix du client:", all_customers)

    @patch("questionary.text")
    def test_prompt_data_customer(self, mock_text):
        responses = {
            "Prénon :": "John",
            "Nom:": "Doe",
            "Email:": "john.doe@example.com",
            "Téléphone:": "1234567890",
            "Entreprise:": "Company Inc."
        }

        def mock_ask(text):
            return responses.get(text, "")

        mock_text.return_value = MagicMock(ask=lambda: mock_ask(mock_text.call_args[0][0]))

        # Appel à la méthode avec les valeurs attendues
        data = CustomerView.prompt_data_customer()

        # Vérification du résultat
        self.assertEqual(data, {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '1234567890',
            'company_name': 'Company Inc.'
        })

    @patch('rich.console.Console.print')
    def test_display_list_customers(self, mock_print):
        # Mock des clients
        mock_customers = [
            MagicMock(first_name='John', last_name='Doe', company_name='Acme',
                      phone='123456789', email='john.doe@example.com', commercial=None,
                      creation_time=datetime(2023, 1, 1), update_time=datetime(2023, 2, 1))
        ]

        # Appel de la méthode
        CustomerView.display_list_customers(mock_customers)

        # Vérifier que la console a bien imprimé
        mock_print.assert_called()

    @patch("questionary.select")
    def test_prompt_customers(self, mock_select):
        # Mock des données du client
        mock_customer = MagicMock()
        mock_customer.first_name = "John"
        mock_customer.last_name = "Doe"
        all_customers = [mock_customer]
        mock_select.return_value.ask.return_value = "John Doe"

        result = CustomerView.prompt_customers(all_customers)

        self.assertEqual(result, mock_customer)
        mock_select.assert_called_once_with(
            "Choix du client:",
            choices=["John Doe"],
        )

    @patch("questionary.confirm")
    def test_prompt_confirm_commercial(self, mock_confirm):
        # Mock de la réponse de confirmation
        mock_confirm.return_value.ask.return_value = True

        result = CustomerView.prompt_confirm_commercial()

        self.assertTrue(result)
        mock_confirm.assert_called_once_with(
            "Souhaitez-vous ajouter un commercial associé à ce client ?"
        )
