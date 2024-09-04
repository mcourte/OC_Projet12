import unittest
from unittest.mock import patch, MagicMock
from rich.console import Console
from views.customer_view import CustomerView


class TestCustomerView(unittest.TestCase):

    @patch('views.prompt_view.PromptView.prompt_select')
    def test_prompt_client(self, mock_prompt_select):
        # Mock data
        all_customers = ["John Doe", "Jane Smith"]
        mock_prompt_select.return_value = "John Doe"

        result = CustomerView.prompt_client(all_customers)

        self.assertEqual(result, "John Doe")
        mock_prompt_select.assert_called_once_with("Choix du client:", all_customers)

    @patch("questionary.text")
    def test_prompt_data_customer(self, mock_text):
        # Mock inputs
        mock_text.side_effect = [
            "John",  # first_name
            "Doe",   # last_name
            "john.doe@example.com",  # email
            "1234567890",  # phone
            "Company Inc."  # company_name
        ]

        with patch('views.regexformat', {
            'all_nospace': [r'^\S+$', "Invalid first name"],
            'all_letters': [r'^[a-zA-Z]+$', "Invalid last name"],
            'email': [r'^\S+@\S+\.\S+$', "Invalid email"],
            'phone': [r'^\d+$', "Invalid phone"],
            'all_space_union': [r'^[\w\s]+$', "Invalid company name"]
        }):
            data = CustomerView.prompt_data_customer()

        self.assertEqual(data, {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '1234567890',
            'company_name': 'Company Inc.'
        })
        mock_text.assert_called()

    @patch.object(Console, 'print')
    def test_display_list_customers(self, mock_print):
        # Mock data
        mock_customer = MagicMock()
        mock_customer.first_name = "John"
        mock_customer.last_name = "Doe"
        mock_customer.company_name = "Company Inc."
        mock_customer.phone = "1234567890"
        mock_customer.email = "john.doe@example.com"
        mock_customer.commercial = MagicMock()
        mock_customer.commercial.username = "JaneDoe"

        CustomerView.display_list_customers([mock_customer])
        mock_print.assert_called()
        # Additional assertions can be made based on how your data is formatted

    @patch("questionary.select")
    def test_prompt_customers(self, mock_select):
        # Mock data
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
        # Mock confirmation response
        mock_confirm.return_value.ask.return_value = True

        result = CustomerView.prompt_confirm_commercial()

        self.assertTrue(result)
        mock_confirm.assert_called_once_with(
            "Souhaitez-vous ajouter un commercial associé à ce client ?"
        )
