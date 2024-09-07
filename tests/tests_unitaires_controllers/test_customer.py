import unittest
from unittest.mock import patch, MagicMock

from controllers.customer_controller import CustomerBase
from config_test import generate_valid_token


class TestCustomerBase(unittest.TestCase):
    def setUp(self):
        # Mock de la session SQLAlchemy
        self.session = MagicMock()
        self.current_user = MagicMock()
        self.current_user.username = 'mcourte'
        self.current_user.role = 'ADM'
        self.session.query().filter_by().first.return_value = None  # Simuler aucun client trouvé

        self.valid_token = generate_valid_token('openclassroom_projet12', self.current_user.username)

    @patch('controllers.customer_controller.CustomerBase.create_customer')
    def test_create_customer(self, mock_create_customer):
        customer_base = CustomerBase(self.session)
        customer_base.current_user = self.current_user

        # Testez la création d'un client
        result = customer_base.create_customer()

        # Vérifiez les assertions
        mock_create_customer.assert_called_once()
        self.assertTrue(result)

    @patch('controllers.customer_controller.CustomerBase.update_customer')
    def test_update_commercial_customer_not_found(self, mock_update_customer):
        customer_base = CustomerBase(self.session)

        # Configurez le mock pour une mise à jour non trouvée
        mock_update_customer.side_effect = Exception("Le Client n'a pas été trouvé dans la base de données.")
        result = None
        try:
            result = customer_base.update_customer(1)  # Passer un ID fictif
        except Exception as e:
            self.assertEqual(str(e), "Le Client n'a pas été trouvé dans la base de données.")

        # Vérifiez les assertions
        mock_update_customer.assert_called_once()
        self.assertIsNone(result)

    @patch('controllers.customer_controller.CustomerBase.update_customer')
    def test_update_customer_success(self, mock_update_customer):
        customer_base = CustomerBase(self.session)
        customer_base.current_user = self.current_user

        # Testez la mise à jour d'un client
        result = customer_base.update_customer()

        # Vérifiez les assertions
        mock_update_customer.assert_called_once()
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
