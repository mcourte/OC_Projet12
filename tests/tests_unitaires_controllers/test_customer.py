import pytest
import sys
import os
from unittest.mock import patch, MagicMock
import unittest
# Déterminez le chemin absolu du répertoire parent
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))

# Ajoutez le répertoire parent au PYTHONPATH
sys.path.insert(0, parent_dir)

from models.entities import Customer
from controllers.customer_controller import CustomerBase
from views.customer_view import CustomerView


class TestCustomerBase(unittest.TestCase):

    @patch('views.console_view.console')
    @patch('models.entities.Customer')
    def test_create_customer(self, mock_customer, mock_console):
        session_mock = MagicMock()
        customer_base = CustomerBase(session_mock)

        # Simule les données du client
        customer_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '1234567890',
            'company_name': 'Doe Inc.',
            'commercial_id': 1
        }

        # Crée un mock pour le client
        customer_mock = MagicMock()
        mock_customer.return_value = customer_mock

        # Appelle la méthode create_customer
        result = customer_base.create_customer(session_mock, customer_data)

        # Vérifie que le client a été créé avec les bonnes valeurs
        mock_customer.assert_called_once_with(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='1234567890',
            company_name='Doe Inc.',
            creation_time=mock_customer.return_value.creation_time,
            update_time=mock_customer.return_value.update_time,
            commercial_id=1
        )

        # Vérifie que le client a été ajouté à la session et commit
        session_mock.add.assert_called_once_with(customer_mock)
        session_mock.commit.assert_called_once()

        # Vérifie que le résultat est bien le client créé
        self.assertEqual(result, customer_mock)

    @patch('views.console_view.console')
    @patch('views.customer_view.CustomerView')
    @patch('models.entities.Customer')
    def test_update_customer_success(self, mock_customer, mock_customer_view, mock_console):
        session_mock = MagicMock()
        customer_base = CustomerBase(session_mock)

        # Simule les données mises à jour
        updated_data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane.doe@example.com',
            'phone': '0987654321',
            'company_name': 'Doe Enterprises'
        }
        mock_customer_view.prompt_data_customer.return_value = updated_data

        # Simule le client existant
        existing_customer_mock = MagicMock()
        session_mock.query().filter_by().first.return_value = existing_customer_mock

        # Appelle la méthode update_customer
        customer_base.update_customer(session_mock, 1)

        # Vérifie que les attributs du client ont été mis à jour
        for key, value in updated_data.items():
            self.assertEqual(getattr(existing_customer_mock, key), value)

        # Vérifie que la session a été commit
        session_mock.commit.assert_called_once()

    @patch('views.console_view.console')
    @patch('models.entities.Customer')
    def test_update_customer_not_found(self, mock_customer, mock_console):
        session_mock = MagicMock()
        customer_base = CustomerBase(session_mock)

        # Simule qu'aucun client n'a été trouvé
        session_mock.query().filter_by().first.return_value = None

        # Vérifie que l'appel de update_customer avec un ID inexistant lève une ValueError
        with self.assertRaises(ValueError):
            customer_base.update_customer(session_mock, 999)

        # Vérifie que la session n'a pas été commit en cas d'erreur
        session_mock.commit.assert_not_called()

    @patch('views.console_view.console')
    @patch('models.entities.Customer')
    def test_update_commercial_customer_success(self, mock_customer, mock_console):
        session_mock = MagicMock()
        current_user_mock = MagicMock()

        # Simule le client existant
        existing_customer_mock = MagicMock()
        session_mock.query().filter_by().first.return_value = existing_customer_mock

        # Appelle la méthode update_commercial_customer
        CustomerBase.update_commercial_customer(current_user_mock, session_mock, 1, 2)

        # Vérifie que le commercial_id du client a été mis à jour
        self.assertEqual(existing_customer_mock.commercial_id, 2)

        # Vérifie que la session a été commit
        session_mock.commit.assert_called_once()

        # Vérifie que le message de succès a été imprimé
        mock_console.print.assert_called_once_with("Commercial ID 2 attribué au client ID 1.", style="bold green")

    @patch('views.console_view.console')
    @patch('models.entities.Customer')
    def test_update_commercial_customer_not_found(self, mock_customer, mock_console):
        session_mock = MagicMock()
        current_user_mock = MagicMock()

        # Simule qu'aucun client n'a été trouvé
        session_mock.query().filter_by().first.return_value = None

        # Vérifie que l'appel de update_commercial_customer avec un ID inexistant lève une ValueError
        with self.assertRaises(ValueError):
            CustomerBase.update_commercial_customer(current_user_mock, session_mock, 999, 2)

        # Vérifie que la session n'a pas été commit en cas d'erreur
        session_mock.commit.assert_not_called()
